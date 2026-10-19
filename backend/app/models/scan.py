import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_name = Column(String(255), nullable=False)
    trigger_type = Column(String(50), default="manual_paste")  # manual_paste, file_upload, zip_upload, git_changed
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    
    total_files = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    
    duration_ms = Column(Integer, default=0)
    cache_hit_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="scans")
    user = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    tool_runs = relationship("ToolRun", back_populates="scan", cascade="all, delete-orphan")
    files = relationship("ScanFile", back_populates="scan", cascade="all, delete-orphan")

class ScanFile(Base):
    __tablename__ = "scan_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    size_bytes = Column(Integer, default=0)
    lines_count = Column(Integer, default=0)
    language = Column(String(50), default="python")
    is_analyzed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scan = relationship("Scan", back_populates="files")
