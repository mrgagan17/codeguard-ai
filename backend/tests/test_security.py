import io
import zipfile
import pytest
from app.core.security import is_safe_path, validate_safe_zip_members, redact_text

def test_is_safe_path_detects_traversal():
    base_dir = "/app/storage"
    assert is_safe_path(base_dir, "/app/storage/file.py") is True
    assert is_safe_path(base_dir, "/app/storage/sub/file.py") is True
    assert is_safe_path(base_dir, "/app/storage/../etc/passwd") is False
    assert is_safe_path(base_dir, "/etc/passwd") is False

def test_zip_slip_protection():
    dest_dir = "C:/temp/sandbox"
    # Create an in-memory ZIP with a malicious entry '../escape.py'
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("../../escape.py", "malicious_code = True")
    
    zip_buffer.seek(0)
    with zipfile.ZipFile(zip_buffer, "r") as zf:
        with pytest.raises(ValueError, match="Malicious archive member detected"):
            validate_safe_zip_members(zf, dest_dir)

def test_redact_text_masks_bearer_token():
    text = "Authorization: Bearer super_secret_token_123456789_abcdef"
    redacted = redact_text(text)
    assert "[REDACTED]" in redacted
    assert "super_secret_token" not in redacted
