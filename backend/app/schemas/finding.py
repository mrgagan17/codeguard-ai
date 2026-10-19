from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import SeverityEnum, CategoryEnum, StatusEnum, ConfidenceEnum

class FindingBase(BaseModel):
    rule_id: str
    title: str
    description: str
    category: CategoryEnum
    severity: SeverityEnum
    confidence: Optional[ConfidenceEnum] = ConfidenceEnum.HIGH
    file_path: str
    start_line: int = Field(default=1, ge=1)
    end_line: int = Field(default=1, ge=1)
    snippet: Optional[str] = None
    tool: str
    why_it_matters: Optional[str] = None
    recommended_remediation: Optional[str] = None
    references: Optional[str] = None
    status: StatusEnum = StatusEnum.OPEN
    status_justification: Optional[str] = None
    suppression_reason: Optional[str] = None

class FindingCreate(FindingBase):
    pass

class FindingResponse(FindingBase):
    id: str
    scan_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class FindingStatusUpdate(BaseModel):
    status: StatusEnum
    justification: Optional[str] = None

class FindingFilter(BaseModel):
    severity: Optional[SeverityEnum] = None
    category: Optional[CategoryEnum] = None
    status: Optional[StatusEnum] = None
    tool: Optional[str] = None
    file_path: Optional[str] = None
    query: Optional[str] = None
