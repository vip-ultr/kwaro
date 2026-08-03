"""Smoke test: kwaro scan runs end to end on a fixture and exercises the math."""
import os
import sqlite3

import pytest

from kwaro.core.models import SprtDecision, Stage
from kwaro.core import verify, graph, loop
from kwaro.__main__ import analyze_file, prove, fix, verify_finding

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "vuln-repo", "app.py")


def test_analyze_finds_secret_and_sqli():
    findings = analyze_file(FIXTURE)
    rules = {f.rule_id for f in findings}
    assert "secrets.hardcoded-secret" in rules
    assert "injection.sql-concat" in rules


def test_bayes_and_sprt_on_real_finding():
    f = analyze_file(FIXTURE)[0]
    prove(f)
    verify_finding(f)
    assert f.posterior > f.prior
    assert f.sprt_decision in (SprtDecision.REAL, SprtDecision.INCONCLUSIVE)


def test_graph_rejects_skipped_prove():
    ok, _ = graph.is_valid_trace([Stage.FIND, Stage.FIX])
    assert ok is False
    ok2, _ = graph.is_valid_trace([Stage.FIND, Stage.PROVE, Stage.FIX, Stage.VERIFY, Stage.DONE])
    assert ok2 is True


def test_loop_variant_terminates():
    findings = analyze_file(FIXTURE)
    trace = loop.run(findings, prove, fix, verify_finding, cap=12)
    assert trace[0] > 0
    assert trace[-1] <= trace[0]
    assert all(trace[i] >= trace[i + 1] for i in range(len(trace) - 1))
