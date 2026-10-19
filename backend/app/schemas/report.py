from pydantic import BaseModel


class ReportExportRequest(BaseModel):
    scan_id: str
    format: str = "json"  # json, csv, markdown, html
    include_code_snippets: bool = True
    include_remediations: bool = True

class SettingItem(BaseModel):
    key: str
    value: str
    description: str | None = None

class SettingUpdateBatch(BaseModel):
    settings: dict[str, str]
