"""Rust/Solana AST rules (Phase A).

Rule families (from Solana audit-firm reporting: neodyme, OWASP Solana Top 10):
  - rust.sol-missing-signer:    state/lamport write without an is_signer /
                                require! / require_keys! guard on the acting
                                account in the same handler.
  - rust.sol-missing-ownership: handler writes config/authority fields or moves
                                funds keyed to an account it never compares
                                against the stored owner.
  - rust.unchecked-arith:       raw + / - / * on u64/u128-ish operands not
                                wrapped in checked_*/saturating_*/wrapping_*.

Heuristics, honestly: tree-sitter gives us structure; the guards we look for
are naming/pattern heuristics like Semgrep CE's, NOT sound analysis. Each rule
reports the function line and a snippet. The CLEAN fixture function
(with require_keys_eq!/is_signer/checked_sub) must produce ZERO findings.

Zero-dep guarantee: this module imports tree-sitter lazily via ast.parser;
when the extra is absent every scan returns [] and regex mode carries on.
"""
from ...analyzers.base import register
from ...core.models import Confidence, Finding, Severity
from ..parser import parse_file, walk

_SIGNER_GUARD_MARKERS = (
    "is_signer",
    "require_signer",
    "check_signer",
    "signer_seeds",
)
_AUTHZ_MARKERS = ("require", "assert")  # require_keys_eq!, assert_eq!, etc.
_ARITH_OK_PREFIXES = ("checked_", "saturating_", "wrapping_")


def _text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf8", "replace")


def _fn_name(node, src) -> str:
    n = node.child_by_field_name("name")
    return _text(src, n) if n else "<anon>"


def _has_guard(fn_node, src, markers) -> bool:
    for n in walk(fn_node):
        if n.type in ("call_expression", "macro_invocation"):
            s = _text(src, n)
            if any(m in s for m in markers):
                return True
        # field access like ctx.accounts.authority.is_signer
        if n.type == "field_expression":
            if any(m in _text(src, n) for m in markers):
                return True
    return False


def _does_state_write(fn_node, src) -> bool:
    for n in walk(fn_node):
        t = n.type
        if t == "assignment_expression" or t == "compound_assignment_expression":
            return True
        if t == "field_expression":
            s = _text(src, n)
            if "try_borrow_mut_lamports" in s:
                return True
    return False


def check_missing_signer(path, tree, src):
    """Lamport/state write in a handler with NO signer guard anywhere."""
    out = []
    for fn in walk(tree.root_node):
        if fn.type != "function_item":
            continue
        if not _does_state_write(fn, src):
            continue
        if _has_guard(fn, src, _SIGNER_GUARD_MARKERS):
            continue
        out.append(Finding(
            title="Missing signer check on state-changing instruction",
            severity=Severity.HIGH,
            cwe="CWE-862",
            rule_id="rust.sol-missing-signer",
            source="static",
            confidence=Confidence.MED,
            file=path,
            line_start=fn.start_point[0] + 1,
            snippet=_text(src, fn).strip().splitlines()[0][:160],
            description=(
                "Function '%s' mutates account state or lamports but contains no "
                "signer verification (is_signer / require! / require_signer). "
                "Anyone can invoke it." % _fn_name(fn, src)
            ),
        ))
    return out


def check_missing_ownership(path, tree, src):
    """Handler assigns an authority/key field from an account it never
    validates against a stored owner (require_keys_eq!/owner comparison)."""
    out = []
    for fn in walk(tree.root_node):
        if fn.type != "function_item":
            continue
        body_text = _text(src, fn.child_by_field_name("body") or fn)
        # does it set an authority-ish field?
        sets_auth = any(k in body_text for k in ("authority =", "admin =", "owner =", ".key()"))
        if not sets_auth:
            continue
        if _has_guard(fn, src, _AUTHZ_MARKERS + ("owner",)):
            continue
        out.append(Finding(
            title="Missing ownership check on privileged field write",
            severity=Severity.HIGH,
            cwe="CWE-284",
            rule_id="rust.sol-missing-ownership",
            source="static",
            confidence=Confidence.MED,
            file=path,
            line_start=fn.start_point[0] + 1,
            snippet=_text(src, fn).strip().splitlines()[0][:160],
            description=(
                "Function '%s' writes an authority/admin field from an account "
                "without comparing it to the stored owner (require_keys_eq!). "
                "An attacker can pass their own account." % _fn_name(fn, src)
            ),
        ))
    return out


def check_unchecked_arith(path, tree, src):
    """Raw binary +/-/* where neither operand path goes through a checked/
    saturating/wrapping call. u64/u128 overflow panics in Rust -> DoS."""
    out = []
    for fn in walk(tree.root_node):
        if fn.type != "function_item":
            continue
        for n in walk(fn):
            if n.type != "binary_expression":
                continue
            op = n.child_by_field_name("operator") or (n.children[1] if len(n.children) > 1 else None)
            if op is None:
                continue
            op_s = _text(src, op)
            if op_s not in ("+", "-", "*"):
                continue
            line = _text(src, src and n).splitlines()[0] if False else None
            seg = _text(src, n)
            # skip if this expression sits inside a checked_/saturating_/wrapping call
            parent_ok = False
            p = n.parent
            while p is not None:
                ps = _text(src, p)
                if any(pre in ps for pre in _ARITH_OK_PREFIXES) or \
                   any(g in ps for g in ("ok_or", "expect(", "unwrap_or")):
                    parent_ok = True
                    break
                if p.type == "function_item":
                    break
                p = p.parent
            if parent_ok:
                continue
            out.append(Finding(
                title="Unchecked arithmetic (overflow/underflow panic)",
                severity=Severity.MEDIUM,
                cwe="CWE-190",
                rule_id="rust.unchecked-arith",
                source="static",
                confidence=Confidence.LOW,
                file=path,
                line_start=n.start_point[0] + 1,
                snippet=seg.strip()[:160],
                description=(
                    "'%s' uses raw arithmetic. In release builds this wraps silently; "
                    "in debug it panics. Use checked_add/checked_sub/saturating_*."
                    % seg.strip()
                ),
            ))
            break  # one report per function keeps noise down
    return out


class RustSolanaAnalyzer:
    name = "rust_solana"
    supports_ast_only = True

    def scan(self, path, lines=None):
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        if ext != "rs":
            return []
        tree, src = parse_file(path)
        if tree is None:
            return []  # extra absent or grammar missing -> regex mode handles nothing here
        out = []
        out.extend(check_missing_signer(path, tree, src))
        out.extend(check_missing_ownership(path, tree, src))
        out.extend(check_unchecked_arith(path, tree, src))
        return out


register(RustSolanaAnalyzer())
