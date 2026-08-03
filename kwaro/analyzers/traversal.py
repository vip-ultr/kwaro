"""Path traversal analyzer (CWE-22)."""
from __future__ import annotations

import re

from .base import Analyzer, Rule, register
from ..core.models import Severity


@register
class Traversal(Analyzer):
    name = "traversal"
    rules = [
        Rule(
            rule_id="open-userpath", cwe="CWE-22", severity=Severity.HIGH,
            regex=re.compile(r"(open|read_file|write_file|os\.path\.join|os\.ReadFile|send_file|fs\.readFile|fs\.readFileSync)\s*\([^)]*(request|params|query|argv|input|user|req\.)", re.IGNORECASE),
            title="Possible path traversal",
            message="A filesystem call uses untrusted input without a base-dir check or normalization. Validate and resolve within an allowed root.",
        ),
        Rule(
            rule_id="double-dot", cwe="CWE-22", severity=Severity.MEDIUM,
            regex=re.compile(r"(path|file|filename|fname)\s*[=:]\s*[^;]*(\.\.[/\\])"),
            title="Possible path traversal (.. in path)",
            message="A path built from input contains '..' segments. Reject or normalize and confine to a root.",
        ),
    ]
