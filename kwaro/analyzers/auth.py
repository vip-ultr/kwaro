"""Auth analyzer: missing auth checks, insecure comparisons, weak hashes (CWE-287/256/328)."""
from __future__ import annotations

import re

from .base import Analyzer, Rule, register
from ..core.models import Severity


@register
class Auth(Analyzer):
    name = "auth"
    rules = [
        Rule(
            rule_id="md5-sha1", cwe="CWE-328", severity=Severity.MEDIUM,
            regex=re.compile(r"(hashlib\.(md5|sha1)|MD5\(|SHA1\(|bcrypt|\.update\(.*digest)\b"),
            title="Weak hash for secrets/passwords",
            message="A broken hash (MD5/SHA1) is used. Use a slow, salted KDF (argon2/scrypt/bcrypt).",
        ),
        Rule(
            rule_id="compare-to-equal", cwe="CWE-697", severity=Severity.MEDIUM,
            regex=re.compile(r"(password|token|secret|hash)\s*==\s*[\"'][^\"']*[\"']|==\s*(password|token|secret)"),
            title="Insecure credential comparison",
            message="Credentials compared with == is not constant-time and may leak via timing. Use a constant-time compare.",
        ),
        Rule(
            rule_id="verify-none", cwe="CWE-287", severity=Severity.HIGH,
            regex=re.compile(r"(jwt|decode)\s*\([^)]*verify\s*=\s*False|options\s*=\s*\{[^}]*verify\s*[:=]\s*False", re.IGNORECASE),
            title="JWT/auth verification disabled",
            message="Token verification is disabled (verify=False). An attacker can forge tokens. Verify signatures.",
        ),
    ]
