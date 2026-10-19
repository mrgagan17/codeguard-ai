from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum, StatusEnum


class FindingBase(BaseModel):
    rule_id: str
    title: str
    description: str
    category: CategoryEnum
    severity: SeverityEnum
    confidence: ConfidenceEnum | None = ConfidenceEnum.HIGH
    file_path: str
    start_line: int = Field(default=1, ge=1)
    end_line: int = Field(default=1, ge=1)
    snippet: str | None = None
    tool: str
    why_it_matters: str | None = None
    recommended_remediation: str | None = None
    references: str | None = None
    status: StatusEnum = StatusEnum.OPEN
    status_justification: str | None = None
    suppression_reason: str | None = None

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
    justification: str | None = None

class FindingFilter(BaseModel):
    severity: SeverityEnum | None = None
    category: CategoryEnum | None = None
    status: StatusEnum | None = None
    tool: str | None = None
    file_path: str | None = None
    query: str | None = None
