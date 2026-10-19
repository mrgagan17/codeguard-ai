from datetime import datetime

from pydantic import BaseModel

from app.schemas.scan import ScanResponse


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    repository_type: str | None = "upload"
    local_path: str | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    scans: list[ScanResponse] = []

    class Config:
        from_attributes = True
