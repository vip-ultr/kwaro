"""kwaro analyzers: registry + file dispatcher.

Importing this package registers every built-in analyzer. Use scan_file() to run
the enabled analyzers over a file's lines, optionally filtered by name or profile.
Zero runtime deps.
"""
from __future__ import annotations

from typing import List, Optional

from .base import Analyzer, Rule, REGISTRY, register, scan_file
from . import secrets, injection, xss, traversal, auth  # noqa: F401  (populates REGISTRY)

# AST-mode analyzer (kwaro[ast] extra). Import is lazy-safe: rust_solana pulls
# tree-sitter only when it actually parses an .rs file; without the extra its
# scan() returns [] and regex analyzers still run. Registered into the SAME
# registry so profiles/pipeline need no special-casing.
try:  # noqa: F401
    from ..ast.rules import rust_solana  # populates REGISTRY with rust_solana
    from ..ast.rules import taint as _taint_rule  # populates REGISTRY with taint_ast
except ImportError:
    pass

__all__ = ["Analyzer", "Rule", "REGISTRY", "register", "scan_file",
           "secrets", "injection", "xss", "traversal", "auth"]


def enabled_names(profile_enable: Optional[List[str]] = None) -> List[str]:
    if profile_enable:
        return [n for n in profile_enable if n in REGISTRY]
    return list(REGISTRY.keys())
