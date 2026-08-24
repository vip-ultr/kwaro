"""kwaro/ast: tree-sitter AST analysis layer (opt-in `kwaro[ast]` extra).

Locked decision L2 (updated): regex is the ALWAYS-available zero-dep default;
tree-sitter is the opt-in `ast` extra. Everything here imports the extra
lazily so the base CLI stays zero-dependency.
"""
