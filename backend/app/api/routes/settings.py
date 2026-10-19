from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.setting import AppSetting
from app.schemas.report import SettingUpdateBatch
from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "ollama_base_url": settings.OLLAMA_BASE_URL,
    "ollama_model": settings.OLLAMA_DEFAULT_MODEL,
    "radon_cc_warn": str(settings.RADON_CC_WARN),
    "radon_cc_high": str(settings.RADON_CC_HIGH),
    "radon_mi_warn": str(settings.RADON_MI_WARN),
    "max_upload_size_mb": str(settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)),
    "cache_enabled": "true" if settings.CACHE_ENABLED else "false",
}

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    """Retrieve current application configuration settings."""
    stored = {s.key: s.value for s in db.query(AppSetting).all()}
    merged = {**DEFAULT_SETTINGS, **stored}
    return {"settings": merged}

@router.post("")
def update_settings(payload: SettingUpdateBatch, db: Session = Depends(get_db)):
    """Update application configuration settings."""
    for key, value in payload.settings.items():
        record = db.query(AppSetting).filter(AppSetting.key == key).first()
        if record:
            record.value = str(value)
        else:
            record = AppSetting(key=key, value=str(value))
            db.add(record)
    db.commit()
    return {"message": "Settings updated successfully."}
