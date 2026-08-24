"""Intraprocedural taint tracking (Phase B).

Scope is HONEST and matches Semgrep CE: WITHIN one function only. Cross-file /
cross-function taint is a later opt-in tier, not claimed here.

Model:
  SOURCE     - untrusted input enters a variable (request args, env, os, DOM).
  PROPAGATOR - assignment / call-argument moves taint to new variables.
  SANITIZER  - a call that cleans the value (escape, parameterize, int()).
  SINK       - dangerous consumption (SQL execute, shell, eval, HTML write).

A finding fires when a SOURCE-tainted variable reaches a SINK with no
SANITIZER on the path. Implemented as per-language source/sink/sanitizer
tables + a generic AST walker (tree-sitter), so adding a language = adding a
table entry, not new logic.

Zero-dep guarantee unchanged: importing this module never pulls tree-sitter;
scan returns [] when the grammar for the file's extension is absent.
"""
from ..core.models import Confidence, Finding, Severity
from .parser import parse_file, walk

# ---------------------------------------------------------------------------
# Per-language tables. Keys are tree-sitter node-type-agnostic TEXT patterns
# matched against call expressions / attribute chains in the source.
# ---------------------------------------------------------------------------

LANGS = {
    "py": {
        "sources": [
            "request.args.get", "request.args", "request.form", "request.json",
            "request.values", "request.data", "request.headers",
            "sys.argv", "os.environ", "input(", "flask.request",
        ],
        "sinks": {
            "execute": Severity.CRITICAL,      # SQL
            "executemany": Severity.CRITICAL,
            "eval": Severity.HIGH,
            "exec": Severity.HIGH,
            "system": Severity.HIGH,
            "popen": Severity.HIGH,
            "subprocess.call": Severity.HIGH,
            "subprocess.run": Severity.HIGH,
            "check_output": Severity.HIGH,
        },
        "sanitizers": [
            "int(", "float(", "escape", "quote(", "shlex.quote",
            "bleach.clean", "parameterized", "?",  # ? = DBAPI placeholder usage
        ],
    },
    "js": {
        "sources": [
            "req.body", "req.query", "req.params", "location.hash",
            "window.location", "process.argv", "document.URL",
            "document.referrer", "localStorage.getItem",
        ],
        "sinks": {
            "innerHTML": Severity.HIGH,
            "outerHTML": Severity.HIGH,
            "document.write": Severity.HIGH,
            "eval": Severity.CRITICAL,
            "setTimeout": Severity.MEDIUM,
            "Function(": Severity.CRITICAL,
        },
        "sanitizers": [
            "encodeURIComponent", "encodeURI", "DOMPurify.sanitize",
            "sanitizeHtml", "parseInt",
        ],
    },
}

_EXT_TO_LANG = {"py": "py", "js": "js", "jsx": "js", "ts": "js", "tsx": "js"}


def _text(src, node):
    return src[node.start_byte:node.end_byte].decode("utf8", "replace")


def _is_sanitized(seg, sanitizers):
    return any(s in seg for s in sanitizers)


def track_function(fn_node, src, lang_table):
    """Return list of (sink_node, sink_text) where tainted data lands."""
    sources = lang_table["sources"]
    sinks = lang_table["sinks"]
    sanitizers = lang_table["sanitizers"]
    tainted = set()
    hits = []

    for node in walk(fn_node):
        if node.type not in ("assignment", "expression_statement", "call_expression",
                             "call", "variable_declarator", "assignment_expression"):
            continue

        seg = _text(src, node)

        # SOURCE: variable assigned from a source pattern
        if node.type in ("assignment", "assignment_expression", "variable_declarator"):
            if any(s in seg for s in sources):
                name_node = node.child_by_field_name("name") or node.child_by_field_name("left")
                if name_node is not None:
                    tainted.add(_text(src, name_node).strip())
                continue

        # SANITIZER on reassignment clears taint for that var
        if node.type in ("assignment", "assignment_expression"):
            if _is_sanitized(seg, sanitizers):
                name_node = node.child_by_field_name("name") or node.child_by_field_name("left")
                if name_node is not None:
                    tainted.discard(_text(src, name_node).strip())
                continue

        # SINK: call whose argument mentions a tainted variable
        if node.type in ("call_expression", "call"):
            fn_part = node.child_by_field_name("function")
            fn_text = _text(src, fn_part) if fn_part is not None else ""
            sink_key = next((k for k in sinks if k.rstrip("(") in fn_text), None)
            if sink_key is None:
                continue
            args = node.child_by_field_name("arguments") or \
                (node.children[-1] if node.children else None)
            arg_text = _text(src, args) if args is not None else ""
            hit_vars = [v for v in tainted if v in arg_text]
            if hit_vars and not _is_sanitized(arg_text, sanitizers):
                hits.append((node, fn_text or sink_key, hit_vars))
    return hits


def scan_taint(path, lines=None):
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    lang = _EXT_TO_LANG.get(ext)
    if lang is None or lang not in LANGS:
        return []
    table = LANGS[lang]
    tree, src = parse_file(path)
    if tree is None:
        return []
    out = []
    seen_lines = set()
    for fn in walk(tree.root_node):
        if fn.type not in ("function_definition", "function_declaration",
                           "method_definition", "arrow_function"):
            continue
        for node, sink_desc, hit_vars in track_function(fn, src, table):
            line = node.start_point[0] + 1
            if line in seen_lines:
                continue
            seen_lines.add(line)
            sev = next((s for k, s in table["sinks"].items()
                        if k.rstrip("(") in sink_desc), Severity.HIGH)
            out.append(Finding(
                title="Tainted data reaches %s" % sink_desc.strip(),
                severity=sev,
                cwe="CWE-20",
                rule_id="taint.%s-flow" % lang,
                source="static",
                confidence=Confidence.HIGH,
                file=path,
                line_start=line,
                snippet=_text(src, node).strip().splitlines()[0][:160],
                description=(
                    "Intraprocedural data flow: untrusted input (%s) reaches the "
                    "%s sink without passing a sanitizer." %
                    (", ".join(sorted(hit_vars)), sink_desc.strip())
                ),
            ))
    return out
