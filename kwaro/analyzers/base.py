"""kwaro analyzers: base interface + registry.

An Analyzer is a pure-Python, zero-dep static check that yields Finding objects.
Each rule is (regex, Finding template). Analyzers are deterministic pre-filters:
they reduce false positives before any model triage (L2 hybrid model).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional

from ..core.models import Finding, Severity, Confidence


@dataclass
class Rule:
    rule_id: str
    cwe: str
    severity: Severity
    regex: "re.Pattern"
    title: str
    message: str
    # optional: only fire on these file extensions (None = all)
    extensions: Optional[tuple] = None
    confidence: Confidence = Confidence.MED


class Analyzer:
    name: str = "base"
    rules: List[Rule] = []

    def scan(self, path: str, lines: List[str]) -> List[Finding]:
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        out: List[Finding] = []
        for i, line in enumerate(lines, 1):
            for rule in self.rules:
                if rule.extensions and ext not in rule.extensions:
                    continue
                m = rule.regex.search(line)
                if not m:
                    continue
                out.append(Finding(
                    title=rule.title,
                    severity=rule.severity,
                    cwe=rule.cwe,
                    rule_id=f"{self.name}.{rule.rule_id}",
                    source="static",
                    confidence=rule.confidence,
                    file=path,
                    line_start=i,
                    snippet=line.strip()[:160],
                    description=rule.message,
                ))
        return out


# registry filled by analyzers/__init__.py
REGISTRY: dict[str, Analyzer] = {}


def register(a) -> Analyzer:
    inst = a() if isinstance(a, type) else a
    REGISTRY[inst.name] = inst
    return inst


def scan_file(path: str, lines: List[str], only: Optional[List[str]] = None) -> List[Finding]:
    """Run selected analyzers (or all) over a file's lines."""
    out: List[Finding] = []
    names = only or list(REGISTRY.keys())
    for name in names:
        a = REGISTRY.get(name)
        if a:
            out.extend(a.scan(path, lines))
    return out
