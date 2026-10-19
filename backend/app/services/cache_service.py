import hashlib
from typing import Any

from app.core.config import settings
from app.schemas.finding import FindingCreate


class AnalysisCacheService:
    def __init__(self):
        # In-memory fast cache; can also be stored on disk or SQLite
        self._memory_cache: dict[str, list[dict[str, Any]]] = {}

    def compute_cache_key(self, tool_name: str, file_path: str, content: str, tool_version: str) -> str:
        h = hashlib.sha256()
        h.update(tool_name.encode())
        h.update(tool_version.encode())
        h.update(file_path.encode())
        h.update(content.encode())
        return h.hexdigest()

    def get_cached_findings(self, cache_key: str) -> list[FindingCreate] | None:
        if not settings.CACHE_ENABLED:
            return None
        cached = self._memory_cache.get(cache_key)
        if cached is not None:
            return [FindingCreate(**item) for item in cached]
        return None

    def store_cached_findings(self, cache_key: str, findings: list[FindingCreate]):
        if not settings.CACHE_ENABLED:
            return
        self._memory_cache[cache_key] = [f.model_dump() for f in findings]

    def clear(self):
        self._memory_cache.clear()

cache_service = AnalysisCacheService()
