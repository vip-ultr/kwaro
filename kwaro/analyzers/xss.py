"""XSS analyzer: reflected/Stored cross-site scripting (CWE-79).

Fires on web languages only (HTML/JS/TS/JSX/Vue/PHP) where untrusted input is
rendered without escaping.
"""
from __future__ import annotations

import re

from .base import Analyzer, Rule, register
from ..core.models import Severity

WEB_EXT = ("html", "js", "ts", "jsx", "tsx", "vue", "php", "ejs", "hbs")


@register
class Xss(Analyzer):
    name = "xss"
    rules = [
        Rule(
            rule_id="innerhtml", cwe="CWE-79", severity=Severity.MEDIUM,
            extensions=WEB_EXT,
            regex=re.compile(r"(innerHTML|outerHTML|document\.write|insertAdjacentHTML)\s*=[^;]*(\+|request|params|query|location|userInput)", re.IGNORECASE),
            title="Possible XSS (untrusted input into innerHTML)",
            message="User input is written to the DOM without escaping. Use textContent or a sanitizer.",
        ),
        Rule(
            rule_id="vhtml-bind", cwe="CWE-79", severity=Severity.MEDIUM,
            extensions=WEB_EXT,
            regex=re.compile(r"(v-html|=.*\b(req|params|query|input)\b.*>|dangerouslySetInnerHTML)"),
            title="Possible XSS (framework HTML binding of untrusted data)",
            message="A framework binds untrusted data as HTML. Escape or sanitize before rendering.",
        ),
    ]
