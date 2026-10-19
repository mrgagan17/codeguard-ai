
import radon.complexity as cc
import radon.metrics as mi

from app.analyzers.base import BaseAnalyzer
from app.core.config import settings
from app.core.logging import logger
from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum
from app.schemas.finding import FindingCreate


class RadonAnalyzer(BaseAnalyzer):
    name: str = "radon"
    display_name: str = "Radon Complexity & Maintainability Analyzer"
    version: str = "6.0.1"
    is_available: bool = True
    enabled: bool = True
    description: str = "Measures cyclomatic complexity and maintainability index to highlight hard-to-maintain code blocks."

    def check_availability(self) -> bool:
        import importlib.util
        self.is_available = importlib.util.find_spec("radon") is not None
        return self.is_available

    def analyze(self, files: list[tuple[str, str]], base_dir: str) -> list[FindingCreate]:
        findings: list[FindingCreate] = []

        for rel_path, content in files:
            if not rel_path.endswith((".py", ".pyw")) or not content:
                continue

            # 1. Cyclomatic Complexity
            try:
                blocks = cc.cc_visit(content)
                for block in blocks:
                    comp = block.complexity
                    if comp >= settings.RADON_CC_WARN:
                        is_critical = comp >= settings.RADON_CC_HIGH
                        sev = SeverityEnum.HIGH if is_critical else SeverityEnum.MEDIUM
                        
                        # Snippet preview
                        lines = content.splitlines()
                        start_idx = max(0, block.lineno - 1)
                        end_idx = min(len(lines), block.endline)
                        snippet = "\n".join(lines[start_idx:min(start_idx + 8, end_idx)])

                        findings.append(FindingCreate(
                            rule_id=f"radon-cc-{'high' if is_critical else 'warn'}",
                            title=f"High Cyclomatic Complexity in '{block.name}' (Score: {comp})",
                            description=f"Function or method '{block.name}' has a cyclomatic complexity of {comp}. Functions with complexity >= {settings.RADON_CC_WARN} have many branching paths.",
                            category=CategoryEnum.COMPLEXITY,
                            severity=sev,
                            confidence=ConfidenceEnum.HIGH,
                            file_path=rel_path,
                            start_line=block.lineno,
                            end_line=block.endline,
                            snippet=snippet,
                            tool=self.name,
                            why_it_matters="High cyclomatic complexity strongly correlates with higher defect rates, lower testability, and elevated risk during maintenance.",
                            recommended_remediation="Decompose the function into smaller, single-purpose helper functions or use polymorphism/dispatch tables to simplify branching logic.",
                            references="https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity"
                        ))
            except Exception as e:
                logger.debug(f"Radon CC analysis failed for {rel_path}: {e}")

            # 2. Maintainability Index
            try:
                mi_score = mi.mi_visit(content, multi=True)
                if mi_score < settings.RADON_MI_WARN:
                    findings.append(FindingCreate(
                        rule_id="radon-mi-low",
                        title=f"Low Maintainability Index ({mi_score:.1f}/100)",
                        description=f"File {rel_path} scored {mi_score:.1f} on the Radon Maintainability Index (Grade C: Difficult to maintain).",
                        category=CategoryEnum.COMPLEXITY,
                        severity=SeverityEnum.MEDIUM,
                        confidence=ConfidenceEnum.HIGH,
                        file_path=rel_path,
                        start_line=1,
                        end_line=min(20, len(content.splitlines()) or 1),
                        snippet=None,
                        tool=self.name,
                        why_it_matters="Maintainability Index combines Halstead volume, Cyclomatic Complexity, and lines of code. Scores below 20 indicate severe refactoring debt.",
                        recommended_remediation="Refactor large monolithic modules into modular components and reduce cyclomatic complexity.",
                        references="https://radon.readthedocs.io/en/latest/intro.html#maintainability-index"
                    ))
            except Exception as e:
                logger.debug(f"Radon MI analysis failed for {rel_path}: {e}")

        return findings
