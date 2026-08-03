# kwaro - Language Coverage Matrix

This matrix is the honest, eval-generated record of what kwaro can actually find,
per language and per analysis mode. It is filled in as each language's seeded
fixture passes `tests/test_eval.py` (L13). Nothing here is claimed before its eval
is green. See [`plan-phase8.md`](plan-phase8.md) for the build sequence.

Status legend: `shipped` (eval green), `partial`, `planned`.

| Language | Analysis mode | Rule families | Status |
| --- | --- | --- | --- |
| Python | regex | secrets, SQLi, XSS, traversal, weak crypto | shipped |
| JavaScript / TypeScript | regex | secrets, SQLi, XSS, traversal | shipped |
| Go | regex | secrets, SQLi, traversal | shipped |
| Java | regex | secrets, SQLi, traversal | shipped |
| PHP | regex | secrets, SQLi, XSS, traversal | shipped |
| Solidity | regex | secrets | shipped |
| Rust | regex | secrets, weak crypto | shipped |
| Rust (Solana) | ast (planned) | missing signer check, missing ownership check, unchecked arithmetic, account confusion | planned |
| Python | ast (planned) | + taint: source -> sink (SQL/Shell/XSS) | planned |
| JavaScript/TS | ast (planned) | + taint (XSS/DOM, prototype pollution) | planned |
| Go | ast (planned) | + taint | planned |
| Solidity | ast (planned) | reentrancy, unchecked math, tx-origin | planned |
| C / C++ | ast (planned) | buffer/integer issues | planned |

Notes:
- "regex" mode is always available, zero-dependency. It is fast and broad but shallow.
- "ast" mode requires the `kwaro[ast]` extra (tree-sitter + grammars) and enables
  per-language queries + intraprocedural taint. See locked decision L2.
- We target Semgrep-Community-Edition-class breadth, not whole-program CodeQL depth,
  in v1. We do not claim soundness.
