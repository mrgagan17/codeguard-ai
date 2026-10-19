from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.scan import ScanResponse

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    repository_type: Optional[str] = "upload"
    local_path: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    scans: List[ScanResponse] = []

    class Config:
        from_attributes = True
