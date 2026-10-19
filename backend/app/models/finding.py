import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rule_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # security, quality, style, complexity, secret, bug_risk
    severity = Column(String(20), nullable=False, index=True)  # Critical, High, Medium, Low, Informational
    confidence = Column(String(20), default="High")            # High, Medium, Low, None
    
    file_path = Column(String(1024), nullable=False, index=True)
    start_line = Column(Integer, nullable=False, default=1)
    end_line = Column(Integer, nullable=False, default=1)
    
    snippet = Column(Text, nullable=True)                      # Minimized & redacted evidence
    tool = Column(String(50), nullable=False, index=True)       # ruff, bandit, radon, ast, secret, semgrep
    
    why_it_matters = Column(Text, nullable=True)
    recommended_remediation = Column(Text, nullable=True)
    references = Column(Text, nullable=True)                   # JSON or semicolon-separated URLs
    
    status = Column(String(30), default="open", index=True)     # open, accepted, fixed, false_positive, resolved
    status_justification = Column(Text, nullable=True)
    suppression_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    scan = relationship("Scan", back_populates="findings")
    fix_suggestions = relationship("FixSuggestion", back_populates="finding", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_findings_scan_severity", "scan_id", "severity"),
        Index("idx_findings_scan_status", "scan_id", "status"),
    )
