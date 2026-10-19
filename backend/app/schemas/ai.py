from typing import Optional, List
from pydantic import BaseModel

class ExplainFindingRequest(BaseModel):
    finding_id: str
    custom_model: Optional[str] = None

class ExplainFindingResponse(BaseModel):
    finding_id: str
    explanation: str
    why_it_matters: str
    is_ai_generated: bool
    model_used: Optional[str] = None
    confidence_note: str

class FixSuggestionRequest(BaseModel):
    finding_id: str
    custom_model: Optional[str] = None

class FixSuggestionResponse(BaseModel):
    id: str
    finding_id: str
    original_code: str
    suggested_code: str
    patch_diff: str
    explanation: str
    trade_offs: Optional[str] = None
    suggested_tests: Optional[str] = None
    is_ai_generated: bool
    model_used: Optional[str] = None

class OllamaStatusResponse(BaseModel):
    available: bool
    url: str
    current_model: str
    installed_models: List[str] = []
    message: str
