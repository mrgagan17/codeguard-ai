from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.finding import (
    FindingResponse,
    FindingStatusUpdate,
    FindingFilter
)
from app.schemas.common import SeverityEnum, CategoryEnum, StatusEnum
from app.schemas.ai import ExplainFindingResponse, FixSuggestionResponse
from app.services.finding_service import FindingService
from app.services.ai_service import AIService

router = APIRouter(tags=["Findings"])

@router.get("/scans/{scan_id}/findings")
def list_scan_findings(
    scan_id: str,
    severity: Optional[SeverityEnum] = None,
    category: Optional[CategoryEnum] = None,
    status: Optional[StatusEnum] = None,
    tool: Optional[str] = None,
    file_path: Optional[str] = None,
    query: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve findings for a specific scan with comprehensive filtering and pagination."""
    filter_obj = FindingFilter(
        severity=severity,
        category=category,
        status=status,
        tool=tool,
        file_path=file_path,
        query=query
    )
    findings, total = FindingService.get_findings_for_scan(
        db=db,
        scan_id=scan_id,
        filters=filter_obj,
        skip=skip,
        limit=limit
    )
    return {
        "scan_id": scan_id,
        "total": total,
        "skip": skip,
        "limit": limit,
        "findings": [FindingResponse.model_validate(f) for f in findings]
    }

@router.get("/findings/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: str,
    db: Session = Depends(get_db)
):
    finding = FindingService.get_finding_by_id(db, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return finding

@router.patch("/findings/{finding_id}/status", response_model=FindingResponse)
def update_status(
    finding_id: str,
    payload: FindingStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update finding status (open, accepted, fixed, false_positive, resolved) with optional justification."""
    finding = FindingService.update_finding_status(db, finding_id, payload)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return finding

@router.post("/findings/{finding_id}/explain", response_model=ExplainFindingResponse)
async def explain_finding(
    finding_id: str,
    custom_model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Explain why this finding matters and how to address it, utilizing Ollama or verified rules."""
    finding = FindingService.get_finding_by_id(db, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return await AIService.explain_finding(db, finding, custom_model=custom_model)

@router.post("/findings/{finding_id}/suggest-fix", response_model=FixSuggestionResponse)
async def suggest_fix(
    finding_id: str,
    custom_model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate or retrieve a safe unified diff patch and remediation for this finding."""
    finding = FindingService.get_finding_by_id(db, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return await AIService.suggest_fix(db, finding, custom_model=custom_model)
