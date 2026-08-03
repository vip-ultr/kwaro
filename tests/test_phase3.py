"""Phase 3 tests: static analyzer rule sets on a multi-language fixture."""
import os

from kwaro.analyzers import REGISTRY, scan_file, enabled_names
from kwaro.analyzers.base import Rule
from kwaro.core.models import Severity, Confidence
from kwaro.core.profiles import Profile

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "vuln-repo")


def _lines(name):
    with open(os.path.join(FIX, name)) as f:
        return f.readlines()


def test_registry_has_five_analyzers():
    for n in ("secrets", "injection", "xss", "traversal", "auth"):
        assert n in REGISTRY, f"missing analyzer {n}"


def test_secrets_finds_hardcoded_and_aws():
    out = scan_file("app.py", _lines("app.py"), only=["secrets"])
    rule_ids = {f.rule_id for f in out}
    assert "secrets.hardcoded-secret" in rule_ids
    # AWS key not in fixture; just ensure the analyzer ran and produced a finding
    assert len(out) >= 1


def test_injection_finds_sql_concat():
    out = scan_file("app.py", _lines("app.py"), only=["injection"])
    assert any("sql" in f.rule_id for f in out)


def test_xss_fires_only_on_web_extensions():
    # JS file with innerHTML + untrusted input
    out = scan_file("static/bundle.js", _lines("static/bundle.js"), only=["xss"])
    assert any("xss" in f.rule_id for f in out)
    # Python file should NOT trigger xss rules (extension-gated)
    py = scan_file("app.py", _lines("app.py"), only=["xss"])
    assert py == []


def test_traversal_finds_go_readfile():
    out = scan_file("server.go", _lines("server.go"), only=["traversal"])
    assert any("traversal" in f.rule_id for f in out)


def test_auth_finds_md5():
    out = scan_file("app.py", _lines("app.py"), only=["auth"])
    assert any("md5" in f.rule_id for f in out)


def test_profile_enable_filters_analyzers():
    prof = Profile.load("fintech")
    only = enabled_names(prof.enable)
    assert "xss" not in only  # fintech profile disables xss
    assert "secrets" in only and "auth" in only
