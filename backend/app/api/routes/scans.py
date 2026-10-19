import os
import io
import zipfile
import tempfile
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scan import Scan
from app.schemas.scan import (
    ScanResponse,
    ScanDetailResponse,
    ScanCreateSnippet,
    ScanCreateMulti
)
from app.services.scan_service import ScanService
from app.services.git_service import GitService
from app.core.security import validate_safe_zip_members, is_safe_path
from app.core.config import settings
from app.core.auth import get_current_user, get_current_user_optional
from app.models.user import User
from sqlalchemy import or_

router = APIRouter(prefix="/scans", tags=["Scans"])

@router.post("", response_model=ScanResponse)
def create_snippet_scan(
    payload: ScanCreateSnippet,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Analyze a pasted code snippet."""
    if not payload.code or not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")
    
    files = [("snippet.py", payload.code)]
    scan = ScanService.execute_scan(
        db=db,
        target_name=payload.name or "Snippet Review",
        trigger_type="manual_paste",
        files=files,
        user_id=current_user.id if current_user else None
    )
    return scan

@router.post("/multi", response_model=ScanResponse)
def create_multi_file_scan(
    payload: ScanCreateMulti,
    db: Session = Depends(get_db)
):
    """Analyze multiple files provided as JSON payloads."""
    if not payload.files:
        raise HTTPException(status_code=400, detail="At least one file must be provided.")
    
    file_list = [(f.file_path, f.content) for f in payload.files]
    scan = ScanService.execute_scan(
        db=db,
        target_name=payload.name or "Multi-file Review",
        trigger_type="manual_multi",
        files=file_list,
        project_id=payload.project_id
    )
    return scan

@router.post("/upload", response_model=ScanResponse)
async def upload_files_scan(
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form("Uploaded Files Review"),
    project_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Analyze multiple uploaded files with strict size and extension checks."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > settings.MAX_UPLOAD_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum allowed file count is {settings.MAX_UPLOAD_FILES}.")

    extracted_files = []
    total_bytes = 0

    for file in files:
        filename = file.filename or "unknown.py"
        # Verify extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue

        content_bytes = await file.read()
        total_bytes += len(content_bytes)
        if total_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"Total upload size exceeds {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB limit.")

        try:
            content_str = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_str = content_bytes.decode("latin-1")
            except Exception:
                raise HTTPException(status_code=400, detail=f"Could not decode file encoding for: {filename}")

        extracted_files.append((filename, content_str))

    if not extracted_files:
        raise HTTPException(status_code=400, detail="No supported Python files found in upload.")

    scan = ScanService.execute_scan(
        db=db,
        target_name=name or "Uploaded Files Review",
        trigger_type="file_upload",
        files=extracted_files,
        project_id=project_id,
        user_id=current_user.id if current_user else None
    )
    return scan

@router.post("/upload-zip", response_model=ScanResponse)
async def upload_zip_scan(
    zip_file: UploadFile = File(...),
    name: Optional[str] = Form("Repository Archive"),
    project_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Analyze a repository ZIP archive with strict zip-slip and bomb protection."""
    zip_bytes = await zip_file.read()
    if len(zip_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"ZIP exceeds max size limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB.")

    temp_extract = tempfile.mkdtemp(prefix="codeguard_zip_")
    extracted_files = []

    try:
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                # Security check on zip members
                validate_safe_zip_members(z, temp_extract)
                z.extractall(temp_extract)
        except Exception as ze:
            raise HTTPException(status_code=400, detail=f"Invalid or unsafe ZIP archive: {str(ze)}")

        # Collect python files
        for root, dirs, files_in_dir in os.walk(temp_extract):
            # Ignore hidden and virtual env folders
            dirs[:] = [d for d in dirs if d not in (".git", "venv", ".venv", "node_modules", "__pycache__")]
            for f in files_in_dir:
                if f.endswith((".py", ".pyw")):
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, temp_extract).replace("\\", "/")
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="replace") as fh:
                            content = fh.read()
                        extracted_files.append((rel_p, content))
                    except Exception:
                        pass

        if not extracted_files:
            raise HTTPException(status_code=400, detail="No valid Python source files found inside ZIP archive.")

        scan = ScanService.execute_scan(
            db=db,
            target_name=name or zip_file.filename or "ZIP Archive",
            trigger_type="zip_upload",
            files=extracted_files,
            project_id=project_id,
            user_id=current_user.id if current_user else None
        )
        return scan

    finally:
        shutil.rmtree(temp_extract, ignore_errors=True)

@router.post("/git", response_model=ScanResponse)
def scan_git_repository(
    repo_path: str = Form(...),
    base_ref: Optional[str] = Form("HEAD~1"),
    name: Optional[str] = Form("Git Repository Changes"),
    project_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze changed files in an explicitly specified local Git repository."""
    # Safety: ensure path is valid directory on disk
    if not os.path.isdir(repo_path):
        raise HTTPException(status_code=400, detail=f"Specified repository directory not found: {repo_path}")

    try:
        changed_files = GitService.get_changed_files(repo_path, base_ref=base_ref or "HEAD~1")
        if not changed_files:
            raise HTTPException(status_code=400, detail="No changed Python files found in repository to analyze.")

        scan = ScanService.execute_scan(
            db=db,
            target_name=name or f"Git: {os.path.basename(os.path.normpath(repo_path))}",
            trigger_type="git_changed",
            files=changed_files,
            project_id=project_id
        )
        return scan
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("", response_model=List[ScanResponse])
def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """List historical scans ordered by most recent for the authenticated user only."""
    if not current_user:
        return []
    query = db.query(Scan).filter(Scan.user_id == current_user.id)
    if project_id:
        query = query.filter(Scan.project_id == project_id)
    return query.order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()

@router.delete("/history")
def clear_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete all scans and associated audit data for the current user."""
    user_scans = db.query(Scan).filter(Scan.user_id == current_user.id).all()
    count = len(user_scans)
    for s in user_scans:
        db.delete(s)
    db.commit()
    return {"message": "Audit history cleared successfully", "deleted_count": count}

@router.delete("/{scan_id}")
def delete_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific scan belonging to the user."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    if scan.user_id and scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this scan.")
    db.delete(scan)
    db.commit()
    return {"message": "Scan deleted successfully"}

@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_details(
    scan_id: str,
    db: Session = Depends(get_db)
):
    """Get complete scan details including tool runs and findings."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan
