from app.analyzers.secret_analyzer import SecretAnalyzer
from app.core.security import redact_secret, redact_text

def test_secret_redaction_helper():
    raw_secret = "AKIA1234567890ABCDEF"
    redacted = redact_secret(raw_secret, visible_chars=4)
    assert "AKIA" in redacted
    assert "CDEF" in redacted
    assert "[REDACTED]" in redacted
    assert "1234567890AB" not in redacted

def test_secret_analyzer_detects_and_redacts_aws_key():
    analyzer = SecretAnalyzer()
    code = 'AWS_KEY = "AKIA1234567890ABCDEF"\n'
    findings = analyzer.analyze([("config.py", code)], "/tmp")
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "SEC-AWS-KEY"
    assert "AKIA" in f.snippet
    assert "1234567890AB" not in f.snippet
    assert "[REDACTED]" in f.snippet

def test_secret_analyzer_detects_db_uri():
    analyzer = SecretAnalyzer()
    code = 'URI = "postgresql://user:SecretPassword999@localhost:5432/mydb"\n'
    findings = analyzer.analyze([("db.py", code)], "/tmp")
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "SEC-DB-URI"
    assert "SecretPassword999" not in f.snippet
    assert "[REDACTED]" in f.snippet

def test_secret_analyzer_clean_code():
    analyzer = SecretAnalyzer()
    code = 'API_URL = "https://api.github.com/v1/users"\nTIMEOUT = 30\n'
    findings = analyzer.analyze([("clean.py", code)], "/tmp")
    assert len(findings) == 0
