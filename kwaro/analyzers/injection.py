"""Injection analyzer: SQL / command injection via string concatenation (CWE-89/78)."""
from __future__ import annotations

import re

from .base import Analyzer, Rule, register
from ..core.models import Severity


@register
class Injection(Analyzer):
    name = "injection"
    rules = [
        Rule(
            rule_id="sql-concat", cwe="CWE-89", severity=Severity.HIGH,
            regex=re.compile(r"(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)\b.*\+.*", re.IGNORECASE),
            title="Possible SQL injection (string concat into query)",
            message="A SQL string is built by concatenation, which can allow injection. Use parameterized queries.",
        ),
        Rule(
            rule_id="sql-format", cwe="CWE-89", severity=Severity.HIGH,
            # f-string / %-format / .format feeding a query literal
            regex=re.compile(r"(execute|cursor\.execute|query|raw|sql)\s*\([^)]*(\{|%s|%\(|f['\"]).*", re.IGNORECASE),
            title="Possible SQL injection (formatted query)",
            message="A query is built with string formatting. Use bind parameters instead.",
        ),
        Rule(
            rule_id="os-command", cwe="CWE-78", severity=Severity.HIGH,
            regex=re.compile(r"(os\.system|subprocess\.(call|run|Popen|shell)\s*\([^)]*\+|eval\(|exec\()"),
            title="Possible command injection",
            message="User-controlled input may reach a shell/command call. Avoid shell=True and validate input.",
        ),
    ]
