
from pydantic import BaseModel


class ExplainFindingRequest(BaseModel):
    finding_id: str
    custom_model: str | None = None

class ExplainFindingResponse(BaseModel):
    finding_id: str
    explanation: str
    why_it_matters: str
    is_ai_generated: bool
    model_used: str | None = None
    confidence_note: str

class FixSuggestionRequest(BaseModel):
    finding_id: str
    custom_model: str | None = None

class FixSuggestionResponse(BaseModel):
    id: str
    finding_id: str
    original_code: str
    suggested_code: str
    patch_diff: str
    explanation: str
    trade_offs: str | None = None
    suggested_tests: str | None = None
    is_ai_generated: bool
    model_used: str | None = None

class OllamaStatusResponse(BaseModel):
    available: bool
    url: str
    current_model: str
    installed_models: list[str] = []
    message: str
