import re

from app.analyzers.base import BaseAnalyzer
from app.core.security import redact_text
from app.schemas.common import CategoryEnum, ConfidenceEnum, SeverityEnum
from app.schemas.finding import FindingCreate

SECRET_PATTERNS = [
    {
        "id": "SEC-AWS-KEY",
        "name": "AWS Access Key ID",
        "regex": re.compile(r'(?i)\b(AKIA[0-9A-Z]{16})\b'),
        "severity": SeverityEnum.CRITICAL,
        "why": "Leaked AWS Access Key IDs can grant unauthorized cloud infrastructure access.",
        "fix": "Store credentials in environment variables, AWS IAM roles, or AWS Secrets Manager."
    },
    {
        "id": "SEC-GITHUB-PAT",
        "name": "GitHub Personal Access Token",
        "regex": re.compile(r'\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b'),
        "severity": SeverityEnum.CRITICAL,
        "why": "Compromised GitHub tokens allow attackers to read private repositories, tamper with code, or compromise CI/CD pipelines.",
        "fix": "Revoke the token immediately, rotate it, and use GitHub Actions secrets or environment variables."
    },
    {
        "id": "SEC-SLACK-TOKEN",
        "name": "Slack API / Bot Token",
        "regex": re.compile(r'\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b'),
        "severity": SeverityEnum.HIGH,
        "why": "Slack tokens allow unauthorized reading and posting of workplace communications.",
        "fix": "Store Slack bot/user tokens in secure server-side environment variables."
    },
    {
        "id": "SEC-PRIVATE-KEY",
        "name": "Private Cryptographic Key",
        "regex": re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'),
        "severity": SeverityEnum.CRITICAL,
        "why": "Exposed private keys compromise encrypted communications, digital signatures, and SSH access.",
        "fix": "Remove private key files and certificates from source control; use KMS or dedicated vault."
    },
    {
        "id": "SEC-DB-URI",
        "name": "Database Connection String with Credentials",
        "regex": re.compile(r'(?i)(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis):\/\/[a-zA-Z0-9_\-\.]+:(?:([^@\/\s]+))@[a-zA-Z0-9_\-\.]+'),
        "severity": SeverityEnum.CRITICAL,
        "why": "Hardcoded database URLs with passwords allow attackers direct data exfiltration and database destruction.",
        "fix": "Extract database connection strings into encrypted environment configuration."
    },
    {
        "id": "SEC-GENERIC-SECRET",
        "name": "Hardcoded API Key or Secret Assignment",
        "regex": re.compile(r'(?i)\b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|auth[_-]?token|password|passwd|pwd)\s*=\s*["\']([a-zA-Z0-9_\-\.\/+=]{12,120})["\']'),
        "severity": SeverityEnum.HIGH,
        "why": "Hardcoded secrets in source code are committed to version control and exposed to unauthorized parties.",
        "fix": "Use environment variables (e.g. via python-dotenv) or a secret manager instead of hardcoded strings."
    }
]

class SecretAnalyzer(BaseAnalyzer):
    name: str = "secret"
    display_name: str = "Secret & Credential Scanner"
    version: str = "1.0.0"
    is_available: bool = True
    enabled: bool = True
    description: str = "Detects hardcoded secrets, API tokens, private keys, and credentials with automatic safe redaction."

    def check_availability(self) -> bool:
        self.is_available = True
        return True

    def analyze(self, files: list[tuple[str, str]], base_dir: str) -> list[FindingCreate]:
        findings: list[FindingCreate] = []

        for rel_path, content in files:
            if not content:
                continue

            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                # Skip comments and obvious docstrings if they look like examples
                stripped = line.strip()
                if stripped.startswith("#") and "example" in stripped.lower():
                    continue

                for pattern_def in SECRET_PATTERNS:
                    match = pattern_def["regex"].search(line)
                    if match:
                        matched_str = match.group(1) if match.groups() and match.group(1) else match.group(0)
                        
                        # Filter out common placeholders
                        lower_m = matched_str.lower()
                        if any(p in lower_m for p in ["dummy", "fake", "placeholder", "changeme", "your_", "my_secret", "test", "demo"]):
                            continue

                        redacted_snippet = redact_text(line).strip()
                        rule_id = pattern_def["id"]

                        findings.append(FindingCreate(
                            rule_id=rule_id,
                            title=f"Potential Hardcoded Secret: {pattern_def['name']}",
                            description=f"Detected probable hardcoded credential ({pattern_def['name']}). Secret values are masked for security.",
                            category=CategoryEnum.SECRET,
                            severity=pattern_def["severity"],
                            confidence=ConfidenceEnum.HIGH,
                            file_path=rel_path,
                            start_line=line_idx,
                            end_line=line_idx,
                            snippet=redacted_snippet,
                            tool=self.name,
                            why_it_matters=pattern_def["why"],
                            recommended_remediation=pattern_def["fix"],
                            references="https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password"
                        ))
                        # Avoid multiple duplicate alerts on the exact same line for the same pattern
                        break

        return findings
