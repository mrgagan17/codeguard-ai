from typing import List, Dict, Type
from app.analyzers.base import BaseAnalyzer
from app.analyzers.ruff_analyzer import RuffAnalyzer
from app.analyzers.bandit_analyzer import BanditAnalyzer
from app.analyzers.secret_analyzer import SecretAnalyzer
from app.analyzers.radon_analyzer import RadonAnalyzer
from app.analyzers.ast_analyzer import ASTAnalyzer
from app.analyzers.semgrep_analyzer import SemgrepAnalyzer

ANALYZER_CLASSES: List[Type[BaseAnalyzer]] = [
    ASTAnalyzer,
    SecretAnalyzer,
    RuffAnalyzer,
    BanditAnalyzer,
    RadonAnalyzer,
    SemgrepAnalyzer,
]

def get_all_analyzers() -> List[BaseAnalyzer]:
    """Instantiate and return all registered analyzer adapters."""
    return [cls() for cls in ANALYZER_CLASSES]

def get_analyzer_status() -> List[Dict[str, any]]:
    """Return status and availability information for all analyzers."""
    analyzers = get_all_analyzers()
    return [
        {
            "name": a.name,
            "display_name": a.display_name,
            "version": a.version,
            "is_available": a.is_available,
            "enabled": a.enabled,
            "description": a.description
        }
        for a in analyzers
    ]
