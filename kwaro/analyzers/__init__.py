"""kwaro analyzers: registry + file dispatcher.

Importing this package registers every built-in analyzer. Use scan_file() to run
the enabled analyzers over a file's lines, optionally filtered by name or profile.
Zero runtime deps.
"""
from __future__ import annotations

from typing import List, Optional

from .base import Analyzer, Rule, REGISTRY, register, scan_file
from . import secrets, injection, xss, traversal, auth  # noqa: F401  (populates REGISTRY)

__all__ = ["Analyzer", "Rule", "REGISTRY", "register", "scan_file",
           "secrets", "injection", "xss", "traversal", "auth"]


def enabled_names(profile_enable: Optional[List[str]] = None) -> List[str]:
    if profile_enable:
        return [n for n in profile_enable if n in REGISTRY]
    return list(REGISTRY.keys())
