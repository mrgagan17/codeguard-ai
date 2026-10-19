import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Storage & Persistence
    DATABASE_URL: str = "sqlite:///./codeguard.db"
    STORAGE_DIR: str = os.path.abspath("./storage")
    ALLOW_SOURCE_PERSISTENCE: bool = True

    # Security & Auth
    SECRET_KEY: str = "codeguard-ai-super-secret-production-key-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # Upload limits
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MAX_UPLOAD_FILES: int = 150
    ALLOWED_EXTENSIONS: List[str] = [".py", ".pyw", ".txt", ".md", ".json", ".yaml", ".yml"]
    
    # Cache
    CACHE_ENABLED: bool = True
    
    # Analyzer toggles & thresholds
    RADON_CC_WARN: int = 10
    RADON_CC_HIGH: int = 20
    RADON_MI_WARN: float = 20.0
    SEMGREP_ENABLED: bool = False
    
    # Subprocess timeouts
    ANALYZER_TIMEOUT_SECONDS: int = 25
    
    # Ollama Local AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "codellama"
    OLLAMA_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
