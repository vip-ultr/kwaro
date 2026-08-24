# kwaro - Language Coverage Matrix

This matrix is the honest, eval-generated record of what kwaro can actually find,
per language and per analysis mode. It is filled in as each language's seeded
fixture passes its eval tests (L13). Nothing here is claimed before its eval
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
| Rust (Solana) | ast | missing signer check (CWE-862), missing ownership check (CWE-284), unchecked arithmetic (CWE-190) | shipped (Phase A; tests/test_phase8.py) |
| Python | ast + taint | tainted flow into SQL execute / shell / eval, with sanitizer awareness (int(), parameterized) | shipped (Phase B; tests/test_phase8b.py) |
| JavaScript/TS | ast + taint | tainted flow into DOM write / eval, with sanitizer awareness (parseInt, encode*) | shipped (Phase B; tests/test_phase8b.py) |
| Go | ast + taint (planned) | + taint | planned |
| Solidity | ast (planned) | reentrancy, unchecked math, tx-origin | planned |
| C / C++ | ast (planned) | buffer/integer issues | planned |

## Verify loop capability (all languages, engine-level)

- PoC generation: offline placeholder always; model-driven with BYOK provider.
- PoC execution (opt-in `--execute-pocs`, Phase C): runs the generated PoC in a
  process sandbox (no network, timeout, output caps). A confirming PoC is strong
  evidence -> posterior 0.635 and SPRT REAL on seeded flows (verified end to end
  on tests/fixtures/py-web). Without execution, static-only findings stay below
  the kept bar by design - that is honest, not a bug.
- Sandbox honesty: process-level containment, NOT a VM/container. Run untrusted
  PoCs only in a container/VM for adversarial targets.

Notes:
- "regex" mode is always available, zero-dependency. It is fast and broad but shallow.
- "ast" mode requires the `kwaro[ast]` extra (tree-sitter + grammars) and enables
  per-language queries + intraprocedural taint. See locked decision L2.
- Taint scope is INTRAPROCEDURAL only (matches Semgrep CE). Cross-file/cross-function
  taint is a later opt-in tier, not claimed here.
- We target Semgrep-Community-Edition-class breadth, not whole-program CodeQL depth,
  in v1. We do not claim soundness.
