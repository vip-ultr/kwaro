"""Phase 5 tests: SARIF/JSON export + diff-aware rescan (L9) baseline."""
import json
import os

from kwaro.core import export
from kwaro.core.models import Finding, Scan, Severity, Confidence, PocState, SprtDecision, Stage
from kwaro.core.storage import Storage
from kwaro.core.workspace import Workspace


def _f(rule_id="auth.md5", file="app.py", line=3, sev=Severity.MEDIUM,
       posterior=0.05, sprt=SprtDecision.NONE, fp="abc123"):
    f = Finding(title="t", severity=sev, cwe="CWE-1", rule_id=rule_id, source="static",
                confidence=Confidence.MED, file=file, line_start=line, snippet="s",
                description="d")
    f.posterior = posterior
    f.sprt_decision = sprt
    f.fingerprint = fp
    return f


def test_to_json_carries_math_fields():
    scan = Scan(target="/x", profile="generic")
    fs = [_f(), _f(rule_id="injection.sql", sev=Severity.HIGH)]
    data = export.to_json(scan, fs)
    assert data["summary"]["total"] == 2
    assert data["findings"][0]["posterior"] == 0.05
    assert "compositeConfidence" in data["findings"][0]
    assert data["summary"]["bySeverity"]["medium"] == 1
    assert data["summary"]["bySeverity"]["high"] == 1


def test_to_sarif_valid_shape():
    scan = Scan(target="/x", profile="generic")
    fs = [_f()]
    sarif = export.to_sarif(scan, fs)
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "kwaro"
    res = sarif["runs"][0]["results"][0]
    assert res["ruleId"] == "auth.md5"
    assert res["partialFingerprints"]["kwaro/rootCause"] == "abc123"
    # math carried in properties
    assert "posterior" in res["properties"]
    assert res["properties"]["sprtDecision"] == "none"


def test_write_report_creates_file(tmp_path):
    scan = Scan(target="/x", profile="generic")
    fs = [_f()]
    p = str(tmp_path / "r.json")
    export.write_report(scan, fs, "json", p)
    assert json.load(open(p))["summary"]["total"] == 1
    p2 = str(tmp_path / "r.sarif")
    export.write_report(scan, fs, "sarif", p2)
    assert json.load(open(p2))["version"] == "2.1.0"


def test_rescan_baseline_roundtrip(tmp_path):
    store = Storage(str(tmp_path / "t.db"))
    store.save_baseline("git@x", "generic", "abc123", {"a.py": "h1", "b.py": "h2"}, 1.0)
    base = store.load_baseline("git@x", "generic")
    assert base["commit"] == "abc123"
    assert base["hashes"]["a.py"] == "h1"
    # missing target returns None
    assert store.load_baseline("nope", "generic") is None


def test_workspace_diff_targets_local():
    ws = Workspace.from_target("tests/fixtures/vuln-repo")
    # no baseline -> all files
    all_files = ws.diff_targets({})
    assert len(all_files) == len(ws.file_hashes)
    # changed hashes -> only those
    changed = ws.diff_targets({p: "stale" for p in ws.file_hashes})
    assert len(changed) == len(ws.file_hashes)  # all differ from "stale"
    # matching baseline -> none changed
    same = ws.diff_targets(dict(ws.file_hashes))
    assert same == []
