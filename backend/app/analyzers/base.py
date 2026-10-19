from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from app.schemas.finding import FindingCreate
from app.schemas.common import SeverityEnum, CategoryEnum, ConfidenceEnum

class BaseAnalyzer(ABC):
    name: str = "base"
    display_name: str = "Base Analyzer"
    version: str = "1.0.0"
    is_available: bool = True
    enabled: bool = True
    description: str = ""

    def __init__(self):
        self.check_availability()

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if analyzer binary/library is installed and operational."""
        pass

    @abstractmethod
    def analyze(self, files: List[Tuple[str, str]], base_dir: str) -> List[FindingCreate]:
        """
        Analyze a list of (relative_file_path, file_content) files in base_dir.
        Must return normalized FindingCreate instances.
        Must not raise uncaught exceptions to caller.
        """
        pass

    @staticmethod
    def normalize_severity(raw_level: str) -> SeverityEnum:
        """Helper to map analyzer-specific severity to standard SeverityEnum."""
        mapping = {
            "critical": SeverityEnum.CRITICAL,
            "fatal": SeverityEnum.CRITICAL,
            "error": SeverityEnum.HIGH,
            "high": SeverityEnum.HIGH,
            "warning": SeverityEnum.MEDIUM,
            "warn": SeverityEnum.MEDIUM,
            "medium": SeverityEnum.MEDIUM,
            "low": SeverityEnum.LOW,
            "info": SeverityEnum.INFORMATIONAL,
            "informational": SeverityEnum.INFORMATIONAL,
            "note": SeverityEnum.INFORMATIONAL,
        }
        return mapping.get(str(raw_level).lower().strip(), SeverityEnum.MEDIUM)
