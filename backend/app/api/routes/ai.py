from fastapi import APIRouter
from app.schemas.ai import OllamaStatusResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Integration"])

@router.get("/ollama-status", response_model=OllamaStatusResponse)
async def get_ollama_status():
    """Detect whether local Ollama service is running and list available models."""
    return await AIService.check_ollama_status()
