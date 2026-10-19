import os
import re
import zipfile
from pathlib import Path
from typing import List, Tuple

# Common patterns for API keys, tokens, and credentials
COMMON_SECRET_PATTERNS = [
    re.compile(r'(?i)(?:api[_-]?key|apikey|secret|token|password|passwd|pwd|auth_token|access_token|private_key)\s*[:=]\s*["\']([^"\']+)["\']'),
    re.compile(r'(?i)(?:bearer)\s+([A-Za-z0-9\-\._~\+\/]+=*)'),
    re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Access Key ID
    re.compile(r'ghp_[0-9a-zA-Z]{36}'),  # GitHub Personal Access Token
    re.compile(r'github_pat_[0-9a-zA-Z_]{82}'), # GitHub Fine-grained PAT
    re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'),  # Slack Token
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?i)((?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis):\/\/[a-zA-Z0-9_\-\.]+):([^@\/\s"\'\n]+)(@[a-zA-Z0-9_\-\.]+)'),
]

def redact_secret(value: str, visible_chars: int = 4) -> str:
    """Safely redact secret values while showing minimal context."""
    if not value:
        return "[REDACTED]"
    value = value.strip()
    length = len(value)
    if length <= visible_chars * 2:
        return "***[REDACTED]***"
    prefix = value[:visible_chars]
    suffix = value[-visible_chars:]
    return f"{prefix}***[REDACTED]***{suffix}"

def redact_text(text: str) -> str:
    """Search and redact sensitive pattern matches in any snippet or text."""
    if not text:
        return ""
    redacted = text
    for pattern in COMMON_SECRET_PATTERNS:
        def _repl(match):
            full_match = match.group(0)
            if len(match.groups()) == 3:
                return f"{match.group(1)}:{redact_secret(match.group(2))}{match.group(3)}"
            if match.groups():
                secret_val = match.group(1)
                return full_match.replace(secret_val, redact_secret(secret_val))
            return redact_secret(full_match)
        redacted = pattern.sub(_repl, redacted)
    return redacted

def is_safe_path(base_dir: str | Path, target_path: str | Path) -> bool:
    """Verify that target_path resolves strictly inside base_dir (prevents directory traversal)."""
    try:
        base = Path(base_dir).resolve()
        target = Path(target_path).resolve()
        return target == base or base in target.parents
    except Exception:
        return False

def validate_safe_zip_members(zip_ref: zipfile.ZipFile, dest_dir: str | Path) -> List[Tuple[str, int]]:
    """
    Validate that all members of a ZIP archive extract safely into dest_dir:
    - No absolute paths
    - No '..' path traversal components
    - Respect reasonable size bounds
    Returns list of safe member filenames and uncompressed sizes.
    Raises ValueError on unsafe member.
    """
    dest_path = Path(dest_dir).resolve()
    valid_members = []
    
    for member in zip_ref.infolist():
        # Prevent zip bombs: check single file uncompressed size (> 50MB)
        if member.file_size > 50 * 1024 * 1024:
            raise ValueError(f"File {member.filename} exceeds safe decompression limit (50MB)")
        
        # Check filename for traversal
        norm_name = os.path.normpath(member.filename)
        if os.path.isabs(norm_name) or norm_name.startswith("..") or "/../" in norm_name.replace("\\", "/"):
            raise ValueError(f"Malicious archive member detected (path traversal): {member.filename}")
        
        target_file = (dest_path / norm_name).resolve()
        if not (target_file == dest_path or dest_path in target_file.parents):
            raise ValueError(f"Archive entry escapes destination directory: {member.filename}")
            
        valid_members.append((member.filename, member.file_size))
        
    return valid_members
