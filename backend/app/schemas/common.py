from enum import Enum


class SeverityEnum(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

class CategoryEnum(str, Enum):
    SECURITY = "security"
    QUALITY = "quality"
    STYLE = "style"
    COMPLEXITY = "complexity"
    SECRET = "secret"
    BUG_RISK = "bug_risk"

class StatusEnum(str, Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    FIXED = "fixed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"

class ConfidenceEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"
