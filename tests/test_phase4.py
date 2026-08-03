"""Phase 4 tests: ranking (L3), de-duplication (L4), prover (L6), pipeline."""
import os

from kwaro.core import rank, pipeline
from kwaro.core.models import (
    Finding, Scan, Severity, Confidence, PocState, SprtDecision, Stage, Evidence,
)
from kwaro.core.rank import (
    severity_score, composite_confidence, confidence_label, fingerprint,
    dedup_by_root_cause,
)
from kwaro.analyzers.prover import generate_poc


def _f(rule_id="auth.md5", file="app.py", line=3, snippet="h=hashlib.md5(pw)",
       sev=Severity.MEDIUM, source="static", posterior=0.05, poc=PocState.NONE):
    f = Finding(title="x", severity=sev, cwe="CWE-1", rule_id=rule_id, source=source,
                confidence=Confidence.MED, file=file, line_start=line, snippet=snippet,
                description="d")
    f.posterior = posterior
    f.poc_state = poc
    return f


def test_severity_score_bands():
    assert severity_score(Severity.CRITICAL) == 9.5
    assert severity_score(Severity.HIGH) == 7.95
    assert severity_score(Severity.MEDIUM) == 5.45
    assert severity_score(Severity.LOW) == 2.0
    assert severity_score(Severity.INFO) == 0.04


def test_composite_confidence_source_and_poc():
    base = _f(source="static", posterior=0.5)
    model_only = _f(source="model", posterior=0.5)
    # static source should yield higher composite than model-only at same posterior
    assert composite_confidence(base) > composite_confidence(model_only)
    verified = _f(source="static", posterior=0.5, poc=PocState.VERIFIED)
    assert composite_confidence(verified) > composite_confidence(base)


def test_confidence_label_bands():
    assert confidence_label(0.9) == Confidence.HIGH
    assert confidence_label(0.5) == Confidence.MED
    assert confidence_label(0.1) == Confidence.LOW


def test_fingerprint_stable_and_case_insensitive():
    a = _f(file="SRC/App.py", snippet="  SELECT * FROM users  ")
    b = _f(file="src/app.py", snippet="select * from users")
    assert fingerprint(a) == fingerprint(b)  # normalized file + snippet
    c = _f(file="src/app.py", snippet="select * from admins")
    assert fingerprint(a) != fingerprint(c)  # different snippet content


def test_dedup_merges_same_root_cause():
    a = _f(rule_id="auth.md5", file="app.py", line=3, snippet="h=hashlib.md5(pw)")
    b = _f(rule_id="auth.md5", file="app.py", line=3, snippet="h=hashlib.md5(pw)")
    c = _f(rule_id="auth.md5", file="app.py", line=4, snippet="h=hashlib.md5(pw2)")
    out = dedup_by_root_cause([a, b, c])
    assert len(out) == 2  # a,b collapse to one; c distinct by line


def test_prover_generates_placeholder_offline(tmp_path):
    f = _f()
    path = generate_poc(f, str(tmp_path))
    assert os.path.exists(path)
    assert f.poc_state == PocState.GENERATED
    # L6: offline placeholder never claims VERIFIED
    assert f.poc_state != PocState.VERIFIED


def test_pipeline_runs_and_ranks():
    findings = [
        _f(rule_id="auth.md5", file="a.py", line=3, sev=Severity.MEDIUM, posterior=0.05),
        _f(rule_id="injection.sql", file="b.py", line=7, sev=Severity.HIGH, posterior=0.05),
        # duplicate of the first (same root cause) to exercise L4
        _f(rule_id="auth.md5", file="a.py", line=3, sev=Severity.MEDIUM, posterior=0.05),
    ]

    def prove(f): pass
    def fix(f): pass
    def verify_finding(f): pass

    result = pipeline.run_pipeline(findings, prove, fix, verify_finding, cap=12)
    # L4: 3 raw -> 2 unique
    assert len(result["unique"]) == 2
    # L3: ranked by severity desc (HIGH before MEDIUM)
    assert result["ranked"][0].severity == Severity.HIGH
    # graph valid
    assert result["graph_valid"] is True
    # loop variant trace is non-increasing and starts > 0
    assert result["trace"][0] > 0
    assert result["trace"] == sorted(result["trace"], reverse=True)
