import hashlib
import os
import shutil
import tempfile
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.analyzers import get_all_analyzers
from app.core.logging import logger
from app.core.security import is_safe_path
from app.models.finding import Finding
from app.models.scan import Scan, ScanFile
from app.models.tool_run import ToolRun
from app.schemas.common import SeverityEnum
from app.schemas.finding import FindingCreate


class ScanService:
    @staticmethod
    def _deduplicate_findings(findings: list[FindingCreate]) -> list[FindingCreate]:
        """Deduplicate findings based on file path, line range, and rule identifier."""
        seen = set()
        seen_semicolons = set()
        deduped = []
        for f in findings:
            if "semicolon" in f.rule_id.lower() or "semicolon" in f.title.lower():
                semi_key = (f.file_path, f.start_line)
                if semi_key in seen_semicolons:
                    continue
                seen_semicolons.add(semi_key)

            key = (f.file_path, f.start_line, f.end_line, f.rule_id)
            if key not in seen:
                seen.add(key)
                deduped.append(f)
        return deduped

    @classmethod
    def execute_scan(
        cls,
        db: Session,
        target_name: str,
        trigger_type: str,
        files: list[tuple[str, str]],  # (relative_path, content)
        project_id: str | None = None,
        user_id: str | None = None
    ) -> Scan:
        start_time = time.time()

        # Create scan record in pending state
        scan = Scan(
            target_name=target_name,
            trigger_type=trigger_type,
            project_id=project_id,
            user_id=user_id,
            status="running",
            total_files=len(files),
            total_lines=sum(len(content.splitlines()) for _, content in files),
            created_at=datetime.utcnow()
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Create a sandboxed temporary directory for analyzer tools
        temp_dir = tempfile.mkdtemp(prefix=f"codeguard_{scan.id[:8]}_")

        try:
            # Write files to sandbox safely
            for rel_path, content in files:
                norm_rel = os.path.normpath(rel_path).lstrip("/\\")
                full_dest = os.path.join(temp_dir, norm_rel)
                
                # Double-check path safety
                if not is_safe_path(temp_dir, full_dest):
                    logger.warning(f"Skipping unsafe path traversal file: {rel_path}")
                    continue

                os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                with open(full_dest, "w", encoding="utf-8", errors="replace") as f:
                    f.write(content)

                # Persist file metadata
                f_hash = hashlib.sha256(content.encode()).hexdigest()
                scan_file = ScanFile(
                    scan_id=scan.id,
                    file_path=rel_path.replace("\\", "/"),
                    file_hash=f_hash,
                    size_bytes=len(content.encode("utf-8")),
                    lines_count=len(content.splitlines()),
                    language="python" if rel_path.endswith((".py", ".pyw")) else "text"
                )
                db.add(scan_file)

            db.commit()

            # Execute Analyzers
            analyzers = get_all_analyzers()
            all_raw_findings: list[FindingCreate] = []
            cache_hits = 0

            for analyzer in analyzers:
                if not analyzer.enabled or not analyzer.is_available:
                    # Record skipped analyzer
                    tr = ToolRun(
                        scan_id=scan.id,
                        tool_name=analyzer.name,
                        version=analyzer.version,
                        status="skipped" if not analyzer.enabled else "unavailable",
                        duration_ms=0,
                        findings_count=0,
                        error_message="Analyzer not available or disabled"
                    )
                    db.add(tr)
                    continue

                tool_start = time.time()
                tool_findings: list[FindingCreate] = []
                status_str = "success"
                err_msg = None

                try:
                    # Run analyzer
                    tool_findings = analyzer.analyze(files, temp_dir)
                except Exception as e:
                    status_str = "failed"
                    err_msg = str(e)
                    logger.error(f"Analyzer '{analyzer.name}' crashed during scan {scan.id}: {e}")

                tool_duration_ms = int((time.time() - tool_start) * 1000)
                all_raw_findings.extend(tool_findings)

                # Record tool run
                tr = ToolRun(
                    scan_id=scan.id,
                    tool_name=analyzer.name,
                    version=analyzer.version,
                    status=status_str,
                    duration_ms=tool_duration_ms,
                    findings_count=len(tool_findings),
                    error_message=err_msg
                )
                db.add(tr)

            # Deduplicate findings
            final_findings = cls._deduplicate_findings(all_raw_findings)

            # Persist findings
            critical_c = 0
            high_c = 0
            med_c = 0
            low_c = 0
            info_c = 0

            for f in final_findings:
                if f.severity == SeverityEnum.CRITICAL:
                    critical_c += 1
                elif f.severity == SeverityEnum.HIGH:
                    high_c += 1
                elif f.severity == SeverityEnum.MEDIUM:
                    med_c += 1
                elif f.severity == SeverityEnum.LOW:
                    low_c += 1
                elif f.severity == SeverityEnum.INFORMATIONAL:
                    info_c += 1

                finding_model = Finding(
                    scan_id=scan.id,
                    rule_id=f.rule_id,
                    title=f.title,
                    description=f.description,
                    category=f.category.value,
                    severity=f.severity.value,
                    confidence=f.confidence.value if f.confidence else "High",
                    file_path=f.file_path,
                    start_line=f.start_line,
                    end_line=f.end_line,
                    snippet=f.snippet,
                    tool=f.tool,
                    why_it_matters=f.why_it_matters,
                    recommended_remediation=f.recommended_remediation,
                    references=f.references,
                    status="open"
                )
                db.add(finding_model)

            # Update scan record
            total_duration_ms = int((time.time() - start_time) * 1000)
            scan.status = "completed"
            scan.total_findings = len(final_findings)
            scan.critical_count = critical_c
            scan.high_count = high_c
            scan.medium_count = med_c
            scan.low_count = low_c
            scan.info_count = info_c
            scan.duration_ms = total_duration_ms
            scan.cache_hit_count = cache_hits
            scan.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(scan)
            return scan

        except Exception as ex:
            db.rollback()
            scan.status = "failed"
            scan.error_message = str(ex)
            scan.completed_at = datetime.utcnow()
            db.commit()
            logger.error(f"Scan {scan.id} failed: {ex}")
            raise ex
        finally:
            # Clean up sandbox safely
            shutil.rmtree(temp_dir, ignore_errors=True)
