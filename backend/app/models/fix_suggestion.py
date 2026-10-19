import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FixSuggestion(Base):
    __tablename__ = "fix_suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    original_code = Column(Text, nullable=False)
    suggested_code = Column(Text, nullable=False)
    patch_diff = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    trade_offs = Column(Text, nullable=True)
    suggested_tests = Column(Text, nullable=True)
    model_name = Column(String(100), default="deterministic")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    finding = relationship("Finding", back_populates="fix_suggestions")
