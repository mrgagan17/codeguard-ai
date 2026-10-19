from fastapi import APIRouter

from app.analyzers import get_analyzer_status

router = APIRouter()

@router.get("/analyzers", tags=["Analyzers"])
def list_analyzers():
    """List all registered static code analysis tools and their runtime status."""
    return {
        "analyzers": get_analyzer_status()
    }
