"""Phase 5 eval (L13): assert recall on the seeded vuln-repo fixture, report FPs.

The fixture is seeded with one instance of each detector we claim to catch. This
test asserts every seeded rule fires (recall) and that no unexpected rule id shows
up (so our own analyzers don't over-flag). It doubles as the launch demo numbers.
"""
import os

from kwaro.analyzers import scan_file

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "vuln-repo")


def _all_findings():
    out = []
    for root, _, files in os.walk(FIX):
        for fn in files:
            p = os.path.join(root, fn)
            if p.endswith((".py", ".js", ".ts", ".go", ".java", ".php", ".sol",
                           ".rs", ".html", ".jsx", ".vue", ".hbs", ".ejs")):
                out.extend(scan_file(p, open(p, errors="ignore").readlines()))
    return out


# seeded expectations: each detector must fire at least once on the fixture
EXPECTED = {
    "secrets.hardcoded-secret",
    "injection.sql-concat",
    "auth.md5-sha1",
    "xss.innerhtml",
    "traversal.open-userpath",
}


def test_recall_on_fixture():
    found = {f.rule_id for f in _all_findings()}
    missing = EXPECTED - found
    assert not missing, f"recall gap: missing seeded rules {missing}"
    # every expected rule fired
    assert EXPECTED <= found


def test_no_unexpected_findings_false_positives():
    found = {f.rule_id for f in _all_findings()}
    known = {
        "secrets.hardcoded-secret", "secrets.aws-key", "secrets.private-key-block",
        "injection.sql-concat", "injection.sql-format", "injection.os-command",
        "xss.innerhtml", "xss.vhtml-bind",
        "traversal.open-userpath", "traversal.double-dot",
        "auth.md5-sha1", "auth.compare-to-equal", "auth.verify-none",
    }
    unexpected = found - known
    assert not unexpected, f"unexpected rule ids (possible FP): {unexpected}"
