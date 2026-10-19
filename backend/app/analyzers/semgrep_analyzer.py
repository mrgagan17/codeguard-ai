import json
import os
import shutil
import subprocess
import sys

from app.analyzers.base import BaseAnalyzer
from app.core.config import settings
from app.core.logging import logger
from app.core.security import redact_text
from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum
from app.schemas.finding import FindingCreate


class SemgrepAnalyzer(BaseAnalyzer):
    name: str = "semgrep"
    display_name: str = "Semgrep Community Engine"
    version: str = "unknown"
    is_available: bool = False
    enabled: bool = True
    description: str = "Fast, open-source static analysis engine for security vulnerabilities and standard anti-patterns."
    executable_path: str = "semgrep"

    def check_availability(self) -> bool:
        if not settings.SEMGREP_ENABLED:
            self.is_available = True
            self.enabled = False
            self.version = "1.181.0"
            return False

        # Check in active Python venv Scripts directory or system PATH
        candidates = [
            os.path.join(os.path.dirname(sys.executable), "semgrep.exe"),
            os.path.join(os.path.dirname(sys.executable), "semgrep"),
            shutil.which("semgrep.exe"),
            shutil.which("semgrep"),
            "semgrep",
        ]
        
        for candidate in candidates:
            if not candidate:
                continue
            try:
                res = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if res.returncode == 0:
                    self.executable_path = candidate
                    self.version = res.stdout.strip()
                    self.is_available = True
                    return True
            except Exception:
                continue

        self.is_available = False
        return False

    def _map_severity(self, raw_sev: str) -> SeverityEnum:
        raw = raw_sev.upper()
        if raw == "ERROR":
            return SeverityEnum.HIGH
        if raw == "WARNING":
            return SeverityEnum.MEDIUM
        if raw == "INFO":
            return SeverityEnum.LOW
        return SeverityEnum.MEDIUM

    def analyze(self, files: list[tuple[str, str]], base_dir: str) -> list[FindingCreate]:
        if not self.is_available:
            return []

        findings: list[FindingCreate] = []
        try:
            # Point to local offline rule file to prevent network calls
            rule_file = os.path.join(os.path.dirname(__file__), "rules", "semgrep_rules.yaml")
            if os.path.isfile(rule_file):
                config_args = ["--config", rule_file]
            else:
                config_args = ["--config", "auto"]

            cmd = [
                self.executable_path,
                "scan",
                "--json",
                "--quiet",
                "--metrics=off",
                "--disable-version-check",
                "--no-git-ignore",
                "--no-trace",
                *config_args,
                base_dir
            ]

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=5,
                cwd=base_dir
            )

            if res.stdout:
                try:
                    data = json.loads(res.stdout)
                    results = data.get("results", [])
                    for item in results:
                        check_id = item.get("check_id", "semgrep-rule")
                        path = item.get("path", "")
                        rel_path = os.path.relpath(path, base_dir) if path else "source.py"
                        rel_path = rel_path.replace("\\", "/")

                        start = item.get("start", {})
                        end = item.get("end", {})
                        start_line = start.get("line", 1)
                        end_line = end.get("line", start_line)

                        extra = item.get("extra", {})
                        msg = extra.get("message", "Semgrep security finding")
                        raw_sev = extra.get("severity", "WARNING")
                        meta = extra.get("metadata", {})
                        cwe = meta.get("cwe", [])
                        cwe_str = f" ({cwe[0]})" if isinstance(cwe, list) and cwe else ""
                        lines_snippet = redact_text(extra.get("lines", "")).strip()

                        category = CategoryEnum.SECURITY if "security" in check_id.lower() or cwe else CategoryEnum.QUALITY
                        severity = self._map_severity(raw_sev)

                        findings.append(FindingCreate(
                            rule_id=f"semgrep-{check_id}",
                            title=f"[{check_id}] {msg[:80]}{cwe_str}",
                            description=f"Semgrep finding: {msg}",
                            category=category,
                            severity=severity,
                            confidence=ConfidenceEnum.HIGH,
                            file_path=rel_path,
                            start_line=start_line,
                            end_line=end_line,
                            snippet=lines_snippet or None,
                            tool=self.name,
                            why_it_matters="Pattern matches known semantic vulnerability rules defined in Semgrep Community rule packs.",
                            recommended_remediation="Inspect the matched pattern and replace with secure idiomatic alternatives.",
                            references=meta.get("source", "https://semgrep.dev/docs")
                        ))
                except json.JSONDecodeError as jde:
                    logger.debug(f"Semgrep output not parsed as JSON: {jde}")
        except subprocess.TimeoutExpired:
            logger.warning("Semgrep scan timed out.")
        except Exception as e:
            logger.warning(f"Error running Semgrep analyzer: {e}")

        return findings
