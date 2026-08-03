"""Secrets analyzer: hardcoded credentials, API keys, tokens (CWE-798/259/312)."""
from __future__ import annotations

import re

from .base import Analyzer, Rule, register
from ..core.models import Severity


@register
class Secrets(Analyzer):
    name = "secrets"
    rules = [
        Rule(
            rule_id="hardcoded-secret", cwe="CWE-798", severity=Severity.HIGH,
            regex=re.compile(r"(api_key|apikey|secret|password|passwd|token|access_key|private_key)\s*[:=]\s*['\"][A-Za-z0-9!@#$%^&*_\-]{8,}['\"]", re.IGNORECASE),
            title="Possible hardcoded secret",
            message="A literal secret-like value is embedded in source. Move it to an env var or secret manager.",
        ),
        Rule(
            rule_id="aws-key", cwe="CWE-798", severity=Severity.CRITICAL,
            regex=re.compile(r"(AKIA|ASIA)[0-9A-Z]{16}"),
            title="Possible AWS access key ID",
            message="An AWS access key ID pattern was found. Rotate and move to a secret manager.",
        ),
        Rule(
            rule_id="private-key-block", cwe="CWE-321", severity=Severity.CRITICAL,
            regex=re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP)? ?PRIVATE KEY-----"),
            title="Embedded private key",
            message="A private key block is committed to source. This is a high-severity leak.",
        ),
    ]
