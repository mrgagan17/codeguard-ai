import json
import os
import subprocess
import sys

from app.analyzers.base import BaseAnalyzer
from app.core.config import settings
from app.core.logging import logger
from app.core.security import redact_text
from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum
from app.schemas.finding import FindingCreate


class BanditAnalyzer(BaseAnalyzer):
    name: str = "bandit"
    display_name: str = "Bandit Security Scanner"
    version: str = "unknown"
    is_available: bool = False
    enabled: bool = True
    description: str = "Finds common security vulnerabilities and unsafe coding patterns in Python code."

    def check_availability(self) -> bool:
        try:
            res = subprocess.run(
                [sys.executable, "-m", "bandit", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 or "bandit" in res.stdout.lower() or "bandit" in res.stderr.lower():
                out = res.stdout.strip() or res.stderr.strip()
                self.version = out.split()[1] if len(out.split()) > 1 else "1.7+"
                self.is_available = True
                return True
        except Exception as e:
            logger.warning(f"Bandit availability check failed: {e}")
        self.is_available = False
        return False

    def _map_severity(self, raw_sev: str, test_id: str) -> SeverityEnum:
        raw = raw_sev.upper().strip()
        # Elevate critical security patterns
        critical_ids = {"B602", "B301", "B501", "B608"}  # shell injection, pickle deserialization, certificate bypass, SQLi
        if test_id in critical_ids or raw == "CRITICAL":
            return SeverityEnum.CRITICAL
        if raw == "HIGH":
            return SeverityEnum.HIGH
        if raw == "MEDIUM":
            return SeverityEnum.MEDIUM
        return SeverityEnum.LOW

    def _map_confidence(self, raw_conf: str) -> ConfidenceEnum:
        raw = raw_conf.upper().strip()
        if raw == "HIGH":
            return ConfidenceEnum.HIGH
        if raw == "MEDIUM":
            return ConfidenceEnum.MEDIUM
        if raw == "LOW":
            return ConfidenceEnum.LOW
        return ConfidenceEnum.MEDIUM

    def analyze(self, files: list[tuple[str, str]], base_dir: str) -> list[FindingCreate]:
        if not self.is_available:
            return []

        py_files = [f[0] for f in files if f[0].endswith((".py", ".pyw"))]
        if not py_files:
            return []

        findings: list[FindingCreate] = []
        try:
            cmd = [
                sys.executable, "-m", "bandit",
                "-r", base_dir,
                "-f", "json",
                "-q",
                "--exit-zero"
            ]

            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=settings.ANALYZER_TIMEOUT_SECONDS,
                cwd=base_dir
            )

            if res.stdout:
                try:
                    data = json.loads(res.stdout)
                    results = data.get("results", [])
                    for item in results:
                        test_id = item.get("test_id", "B000")
                        test_name = item.get("test_name", "Security Issue")
                        issue_text = item.get("issue_text", "")
                        raw_sev = item.get("issue_severity", "MEDIUM")
                        raw_conf = item.get("issue_confidence", "MEDIUM")
                        filename = item.get("filename", "")
                        
                        rel_path = os.path.relpath(filename, base_dir) if filename else "source.py"
                        rel_path = rel_path.replace("\\", "/")

                        line_num = item.get("line_number", 1)
                        line_range = item.get("line_range", [line_num])
                        start_line = line_range[0] if line_range else line_num
                        end_line = line_range[-1] if line_range else line_num
                        code_snippet = redact_text(item.get("code", "")).strip()

                        cwe_info = item.get("issue_cwe", {})
                        cwe_text = f"CWE-{cwe_info.get('id')}" if cwe_info.get("id") else ""
                        more_info = item.get("more_info", "")

                        severity = self._map_severity(raw_sev, test_id)
                        confidence = self._map_confidence(raw_conf)

                        findings.append(FindingCreate(
                            rule_id=f"bandit-{test_id}",
                            title=f"[{test_id}] {issue_text or test_name}",
                            description=f"Bandit security finding ({test_name}): {issue_text}. {cwe_text}",
                            category=CategoryEnum.SECURITY,
                            severity=severity,
                            confidence=confidence,
                            file_path=rel_path,
                            start_line=start_line,
                            end_line=end_line,
                            snippet=code_snippet or None,
                            tool=self.name,
                            why_it_matters="Potential vulnerability that may expose the system to attack, unauthorized data access, or execution flow manipulation.",
                            recommended_remediation="Validate untrusted input, avoid shell execution, use parameterized queries, and adopt secure cryptography libraries.",
                            references=f"{more_info}; {cwe_info.get('link', '')}".strip("; ")
                        ))
                except json.JSONDecodeError as jde:
                    logger.error(f"Failed to parse Bandit output: {jde}")
        except subprocess.TimeoutExpired:
            logger.warning("Bandit analysis timed out.")
        except Exception as e:
            logger.error(f"Error running Bandit analyzer: {e}")

        return findings
