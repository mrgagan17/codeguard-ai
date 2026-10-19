from datetime import datetime

from pydantic import BaseModel

from app.schemas.finding import FindingResponse


class ScanFileItem(BaseModel):
    file_path: str
    content: str

class ScanCreateSnippet(BaseModel):
    name: str | None = "Snippet Review"
    language: str = "python"
    code: str

class ScanCreateMulti(BaseModel):
    name: str | None = "Multi-file Review"
    project_id: str | None = None
    files: list[ScanFileItem]

class ToolRunResponse(BaseModel):
    tool_name: str
    version: str | None = None
    status: str
    duration_ms: int
    findings_count: int
    error_message: str | None = None

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    id: str
    project_id: str | None = None
    target_name: str
    trigger_type: str
    status: str
    total_files: int
    total_lines: int
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    duration_ms: int
    cache_hit_count: int
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True

class ScanDetailResponse(ScanResponse):
    tool_runs: list[ToolRunResponse] = []
    findings: list[FindingResponse] = []
