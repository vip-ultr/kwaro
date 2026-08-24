"""AST taint analyzer (Phase B): wraps ast.taint.scan_taint as an Analyzer.

Registered like any analyzer; returns [] without the kwaro[ast] extra so the
zero-dep CLI is untouched. Enable via profiles (e.g. generic/fintech) or by
name 'taint_ast'.
"""
from ...analyzers.base import register
from ..taint import scan_taint


class TaintAnalyzer:
    name = "taint_ast"

    def scan(self, path, lines=None):
        return scan_taint(path, lines)


register(TaintAnalyzer())
