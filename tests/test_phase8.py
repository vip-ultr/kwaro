"""Phase A eval (L13): Rust/Solana AST rules on the seeded fixture.

Asserts RECALL: every deliberately seeded vuln class is found. Also asserts
the clean function produces no findings (FP guard). Skips when tree-sitter /
tree-sitter-rust are absent so the core CLI suite stays zero-dependency.
"""
import os

import pytest

rs = pytest.importorskip("tree_sitter_rust")

from kwaro.ast.rules.rust_solana import RustSolanaAnalyzer  # noqa: E402

FIXTURE = os.path.join(
    os.path.dirname(__file__), "fixtures", "rust-solana", "programs", "vault", "src", "lib.rs"
)


def findings():
    return RustSolanaAnalyzer().scan(FIXTURE)


def test_fixture_parses_in_ast_mode():
    fs = findings()
    assert len(fs) > 0, "AST mode must produce findings; grammar missing?"


def test_recall_missing_signer():
    hits = [f for f in findings() if f.rule_id == "rust.sol-missing-signer"]
    lines = {f.line_start for f in hits}
    assert any(19 <= l <= 28 for l in lines), "withdraw_sol signer miss undetected"


def test_recall_missing_ownership():
    hits = [f for f in findings() if f.rule_id == "rust.sol-missing-ownership"]
    assert hits, "set_config ownership miss undetected"
    assert any(29 <= f.line_start <= 38 for f in hits)


def test_recall_unchecked_arith():
    hits = [f for f in findings() if f.rule_id == "rust.unchecked-arith"]
    assert hits, "donate arithmetic miss undetected"
    assert any(39 <= f.line_start <= 47 for f in hits)


def test_clean_function_not_flagged():
    # withdraw_checked spans lines ~48-62; nothing may point inside it
    bad = [f for f in findings() if 48 <= f.line_start <= 70]
    assert not bad, "false positive on the properly-guarded function"
