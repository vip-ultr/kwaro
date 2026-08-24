"""Phase B eval (L13): intraprocedural taint on seeded Python + JS fixtures.

Asserts RECALL: every seeded tainted source->sink flow is found. Asserts the
FP guard: sanitized flows (int()/parameterized, parseInt) produce nothing.
Skips when tree-sitter grammars are absent so the core suite stays zero-dep.
"""
import os

import pytest

pytest.importorskip("tree_sitter_rust")  # any grammar implies the extra is present
from kwaro.ast.taint import scan_taint  # noqa: E402

HERE = os.path.dirname(__file__)
PY_FIXTURE = os.path.join(HERE, "fixtures", "py-web", "app.py")
JS_FIXTURE = os.path.join(HERE, "fixtures", "js-web", "server.js")


def test_py_taint_recall():
    hits = {f.line_start for f in scan_taint(PY_FIXTURE)}
    # VULN 1 SQL (~21), VULN 2 shell (~28), VULN 3 eval (~35)
    assert any(20 <= l <= 23 for l in hits), "SQL flow missed: %s" % hits
    assert any(27 <= l <= 30 for l in hits), "shell flow missed: %s" % hits
    assert any(33 <= l <= 37 for l in hits), "eval flow missed: %s" % hits


def test_py_sanitized_flow_not_flagged():
    hits = [f for f in scan_taint(PY_FIXTURE) if f.line_start >= 38]
    assert not hits, "false positive on int()-sanitized parameterized query"


def test_js_taint_recall():
    hits = {f.line_start for f in scan_taint(JS_FIXTURE)}
    assert any(10 <= l <= 13 for l in hits), "DOM write flow missed: %s" % hits
    assert any(15 <= l <= 18 for l in hits), "eval flow missed: %s" % hits


def test_js_safe_handler_not_flagged():
    hits = [f for f in scan_taint(JS_FIXTURE) if f.line_start >= 20]
    assert not hits, "false positive on parseInt-sanitized handler"


def test_taint_registered_as_analyzer():
    from kwaro.analyzers import REGISTRY
    assert "taint_ast" in REGISTRY
