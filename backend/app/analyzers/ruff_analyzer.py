import json
import os
import subprocess
import sys

from app.analyzers.base import BaseAnalyzer
from app.core.config import settings
from app.core.logging import logger
from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum
from app.schemas.finding import FindingCreate


class RuffAnalyzer(BaseAnalyzer):
    name: str = "ruff"
    display_name: str = "Ruff Linter & Quality Checker"
    version: str = "unknown"
    is_available: bool = False
    enabled: bool = True
    description: str = "Fast Python linter for detecting unused imports, undefined variables, and quality issues."

    def check_availability(self) -> bool:
        try:
            res = subprocess.run(
                [sys.executable, "-m", "ruff", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                self.version = res.stdout.strip().replace("ruff ", "")
                self.is_available = True
                return True
        except Exception as e:
            logger.warning(f"Ruff availability check failed: {e}")
        self.is_available = False
        return False

    def _map_code_to_meta(self, code: str) -> tuple[SeverityEnum, CategoryEnum]:
        """Categorize and assign severity based on Ruff rule prefix."""
        if not code or code in ("SYNTAX-ERROR", "None") or code.startswith("E9") or code.startswith("F7"):
            return SeverityEnum.CRITICAL, CategoryEnum.BUG_RISK
        prefix = code[0] if code else ""
        if code.startswith("F821"):  # Undefined name
            return SeverityEnum.HIGH, CategoryEnum.BUG_RISK
        if code.startswith("F401"):  # Unused import
            return SeverityEnum.LOW, CategoryEnum.QUALITY
        if code.startswith("F841"):  # Unused variable
            return SeverityEnum.LOW, CategoryEnum.QUALITY
        if code.startswith("S"):     # Security rules (flake8-bandit in ruff)
            return SeverityEnum.HIGH, CategoryEnum.SECURITY
        if code.startswith("B"):     # Bugbear
            return SeverityEnum.MEDIUM, CategoryEnum.BUG_RISK
        if prefix in ("E", "W"):    # Style errors/warnings
            return SeverityEnum.LOW, CategoryEnum.STYLE
        return SeverityEnum.MEDIUM, CategoryEnum.QUALITY

    def analyze(self, files: list[tuple[str, str]], base_dir: str) -> list[FindingCreate]:
        if not self.is_available:
            return []

        py_files = [f[0] for f in files if f[0].endswith((".py", ".pyw"))]
        if not py_files:
            return []

        findings: list[FindingCreate] = []
        file_map = {f[0].replace("\\", "/"): f[1] for f in files}

        try:
            cmd = [
                sys.executable, "-m", "ruff", "check",
                "--select=E,W,F,B,C,S,I,PL,RUF",
                "--ignore=E501",
                "--output-format=json",
                "--exit-zero",
                "--no-cache",
                base_dir
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
                    for item in data:
                        raw_code = item.get("code")
                        code = raw_code if raw_code is not None else "SYNTAX-ERROR"
                        msg = item.get("message", "Lint finding")
                        filename = item.get("filename", "")
                        
                        # Normalize relative file path
                        rel_path = os.path.relpath(filename, base_dir) if filename else "source.py"
                        rel_path = rel_path.replace("\\", "/")
                        
                        loc = item.get("location", {})
                        end_loc = item.get("end_location", {})
                        start_line = loc.get("row", 1)
                        end_line = end_loc.get("row", start_line)
                        
                        severity, category = self._map_code_to_meta(code)
                        url = item.get("url") or (f"https://docs.astral.sh/ruff/rules/{code.lower()}" if code != "SYNTAX-ERROR" else "https://docs.python.org/3/reference/grammar.html")
                        
                        # Extract snippet from source content
                        snippet = None
                        content = file_map.get(rel_path) or file_map.get(os.path.basename(rel_path))
                        if content:
                            source_lines = content.splitlines()
                            if 1 <= start_line <= len(source_lines):
                                snippet = source_lines[start_line - 1].strip()

                        remediation = "Refactor code to comply with standard Python conventions and resolve the flagged pattern."
                        if code == "E703":
                            remediation = "Remove the trailing semicolon from the end of the statement."

                        findings.append(FindingCreate(
                            rule_id=f"ruff-{code}",
                            title=f"[{code}] {msg}",
                            description=f"Ruff detected rule violation {code}: {msg}",
                            category=category,
                            severity=severity,
                            confidence=ConfidenceEnum.HIGH,
                            file_path=rel_path,
                            start_line=start_line,
                            end_line=end_line,
                            snippet=snippet,
                            tool=self.name,
                            why_it_matters=f"Rule {code} highlights code issues such as unused resources, logic traps, or style violations.",
                            recommended_remediation=remediation,
                            references=url
                        ))
                except json.JSONDecodeError as jde:
                    logger.error(f"Failed to parse Ruff output: {jde}")
        except subprocess.TimeoutExpired:
            logger.warning("Ruff analysis timed out.")
        except Exception as e:
            logger.error(f"Error running Ruff analyzer: {e}")

        return findings
