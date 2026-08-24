"""Lazy tree-sitter parser cache per extension.

Zero-dep guarantee (L1/L2): importing this module NEVER pulls tree-sitter.
`get_parser()` returns None when the grammar for an extension is absent, and
callers fall back to regex mode. Grammars are resolved from installed
`tree_sitter_<lang>` packages via their `language()` entry point.

Supported languages (Phase A order): rust first; python/js/ts/go/java follow
in later phases as grammars + rules land. Unknown extension -> None fast.
"""
import os

# extension -> import name of the grammar package
_GRAMMAR_IMPORTS = {
    "rs": "tree_sitter_rust",
    # wired in later phases:
    "py": "tree_sitter_python",
    "js": "tree_sitter_javascript",
    "jsx": "tree_sitter_javascript",
    "ts": "tree_sitter_typescript",
    "tsx": "tree_sitter_typescript",
    "go": "tree_sitter_go",
    "java": "tree_sitter_java",
}

_parser_cache = {}
_missing = set()


def available_languages():
    """Extensions whose grammar is importable right now."""
    out = []
    for ext, mod in _GRAMMAR_IMPORTS.items():
        try:
            __import__(mod)
            out.append(ext)
        except ImportError:
            pass
    return sorted(set(out))


def get_parser(extension):
    """Return a ready tree-sitter Parser for the extension, or None.

    Results are cached; failures are remembered so repeated misses are cheap
    (a scan touches thousands of files)."""
    if extension not in _GRAMMAR_IMPORTS:
        return None
    if extension in _missing:
        return None
    if extension in _parser_cache:
        return _parser_cache[extension]
    try:
        from tree_sitter import Language, Parser

        mod = __import__(_GRAMMAR_IMPORTS[extension])
        lang = Language(mod.language())
        parser = Parser(lang)
        _parser_cache[extension] = parser
        return parser
    except Exception:
        _missing.add(extension)
        return None


def parse_file(path):
    """Parse a source file into a tree-sitter Tree. Returns (tree, source_bytes)
    or (None, source_bytes) when no grammar / parse failure -> regex fallback."""
    with open(path, "rb") as f:
        src = f.read()
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    parser = get_parser(ext)
    if parser is None:
        return None, src
    try:
        return parser.parse(src), src
    except Exception:
        return None, src


def walk(node):
    """Yield every node in the tree depth-first (including `node`)."""
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(reversed(n.children))
