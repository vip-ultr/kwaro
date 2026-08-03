# Plan: kwaro Phase 8+ - real multi-language depth

Status: researched, planned. Not yet built. This document is the source of truth
for the work that makes kwaro credible on "any codebase," responding directly to
the gap found when `kwaro scan` returned 0 findings on a 74k-line Rust/Solana repo
(it scanned correctly; our 5 regex rules simply don't cover Rust/Solana vuln classes).

## Honest framing (read this first)

kwaro today is a working engine (clone/scan/persist, math spine, profiles, pipeline,
SARIF, browser UI, packaged + installable) with a SHALLOW analysis layer (regex over
8 extensions). That is not "a scanner that works on any codebase." The plan below
closes that gap. It does NOT claim to beat CodeQL. It targets a credible, honest bar:

**Free, local, and Semgrep-Community-Edition-class breadth (tree-sitter AST + intra
procedural taint across the major languages) PLUS the find/prove/fix/verify loop with
visible evidence math, which no free scanner gives you.** CodeQL is deeper (whole-program
DFG/CFG + Datalog) and we are not pretending otherwise. We win on cost, privacy, and the
closed loop, not on raw depth in v1.

### What the research says

- Tree-sitter has official grammars for C, C#, Go, Java, JavaScript, Python, Ruby, Rust,
  Scala, TypeScript, with community grammars for PHP and Solidity. Python bindings
  (`py-tree-sitter` + `tree-sitter-<lang>` wheels) exist, so AST parsing is feasible from
  our pure-Python CLI. Cost: tree-sitter is a NATIVE build (needs a C compiler + grammar
  shared libs), so it cannot stay in the zero-dep CLI. It becomes the `kwaro[ast]` extra.
- Semgrep (CE, free) = tree-sitter AST -> generic AST -> IL -> pattern match + INTRAPROCEDURAL
  taint. Cross-file/cross-function taint is the paid "Pro" tier. CodeQL = per-language
  extractor -> relational DB (AST + DFG + CFG) -> Datalog; deeper but heavier and needs a
  build (or `none` mode). On the OWASP benchmark CodeQL F1 ~74% vs Semgrep ~69%.
- Solana audit firms (neodyme, OWASP Solana Top 10, QuillAudits) repeatedly report the same
  Rust/Solana vuln classes: missing signer check, missing ownership check, account confusion,
  PDA seed collision, unchecked arithmetic/overflow, CPI confusion, reentrancy. All are
  detectable with AST patterns + light data-flow in Rust. None are caught by our 5 generic rules.

## Architecture: regex stays, AST layer added

```
kwaro/
  analyzers/        base + registry (already supports regex mode)
  ast/              NEW - tree-sitter based analysis (kwaro[ast] extra)
    parser.py       lazy per-extension Parser cache; falls back to regex if extra absent
    queries/        .scm query files per language + per rule
    taint.py        intraprocedural source->sink tracker over the AST/CFG
    rules/          AST rule definitions (signer-check, ownership, overflow, sql, xss, ...)
  core/rank, pipeline, ...   unchanged (consume findings either way)
```

- Each analyzer runs in one of two modes, chosen at runtime:
  - `regex` mode (default, ZERO deps): today's behavior. Always available.
  - `ast` mode (needs `kwaro[ast]`): parse with tree-sitter, run queries + taint. Used
    automatically when the extra is installed and the file's language has a grammar.
- The CLI stays zero-dependency. `pipx install kwaro` works unchanged. `pipx install
  "kwaro[ast]"` (or `kwaro scan --ast`) unlocks depth. Locked decision L2 is updated to
  make this split explicit.

## Language priority (build order)

1. **Rust** (your immediate need: the Solana test repo). Also covers generic Rust.
2. **Python + JavaScript/TypeScript** (largest user base; Flask/Django, Node).
3. **Go** (backend/services).
4. **Java** (enterprise).
5. **Solidity** (EVM smart contracts; complements the blockchain profile).
6. **C/C++** and **PHP** (broadest coverage; heavier grammars).

Each language is "done" only when a seeded fixture for it shows 100% recall on its rule
families in `tests/test_eval.py` (L13). No language is claimed before its eval passes.

## Phase A - Rust + blockchain depth (the gap you hit)

Build `kwaro/ast/` with the Rust grammar, then Rust/Solana rules:

- **Missing signer check**: for each instruction handler, find the accounts struct field
  tagged authority/admin (naming heuristic) and confirm the handler verifies
  `accounts.<x>.is_signer` / `require_keys_eq!` / a `check_signer` before any state write
  that depends on it. Missing -> finding.
- **Missing ownership check**: handler reads an account's `owner`/`key` and uses it for
  authorization without comparing to the expected program/owner. Missing -> finding.
- **Unchecked arithmetic**: `a + b` / `a - b` / `a * b` on amounts (u64/u128/lamports) not
  wrapped in `checked_add`/`checked_sub`/`checked_mul`/`saturating_*`. -> finding.
- **Account confusion**: an instruction uses an account where a different, specific account
  is required (heuristic on PDA/key comparisons). -> finding.
- Generic Rust: extend SQLi/XSS/traversal/secrets/weak-hash rules to AST mode so they also
  catch Rust (e.g. `format!` into a shell/`sqlx::query` with unconcatenated input, `std::fs`
  open from a request-derived path).

Deliverable for A: `kwaro scan --profile blockchain` (or `--ast`) returns real findings on
`tests/fixtures/rust-solana/` (seeded with one instance of each above). Eval asserts recall.

## Phase B - Intraprocedural taint (the "real scanner" core)

`kwaro/ast/taint.py`: walk each function's AST, build a small data-flow graph
(source/propagator/sink/sanitizer), and report when an untrusted SOURCE reaches a SINK
without a SANITIZER. This is what stops the "SELECT + docstring" false positive and starts
reporting "user input reaches the query."

- Sources: HTTP params, CLI args, env vars, file reads, `accounts.<x>` user-supplied in
  Solana, `req.body`, `process.argv`, `os.environ`.
- Sinks: SQL execute, shell/`subprocess`, `innerHTML`/DOM write, `std::fs` open,
  `system`, Solana `invoke`/state mutation, `eval`.
- Sanitizers: parameterized query, HTML escape, allowlist, `checked_*` arithmetic.
Scope: intraprocedural in v1 (matches Semgrep CE). Cross-function is a later, opt-in depth
tier, not claimed for v1.

## Phase C - Real prove/fix/verify (the differentiator)

Today `prover.py` writes a placeholder PoC and never runs it (L6 sandbox specced but
unbuilt). Build it for real: generate a minimal failing test/program, run it in a temp dir
with no network + resource/time limits, classify VERIFIED/UNVERIFIED, report the crash
output. This is the "prove" no free scanner does for you locally. Tie the existing chat
fix step to verified findings.

## Phase D - Breadth, honesty, eval

- `docs/coverage.md`: a matrix. Columns: language | analysis mode (regex/ast) | rule families
  covered | status (shipped/partial/planned). Generated from the eval, not asserted.
- Extend `tests/fixtures/` with one seeded repo per language (`rust-solana`, `py-web`,
  `go-svc`, ...). `tests/test_eval.py` asserts recall per language and flags FPs.
- README/scan output states coverage honestly: "AST depth for: Rust, Python, JS. Regex
  only for: Go, Java, C/C++, PHP, Solidity. Planned: <list>." No overclaiming.

## What we will NOT claim

- We will not claim to "beat CodeQL" on deep multi-step taint in v1.
- We will not claim a language is supported until its eval passes.
- We will not claim soundness (tree-sitter taint is heuristic, like Semgrep CE).

## Sequencing summary

A (Rust/blockchain + tree-sitter wiring) -> B (taint) -> C (real PoC) -> D (matrix + eval).
Each phase ends runnable, verified by a seeded fixture + green test, committed, and the
docs updated. A fresh session can resume from BUILD.md.

## Effort reality

This is the real SAST build, not a tweak. Phase A alone is several focused sessions
(grammar wiring, Rust queries, Solana rules, fixture, eval). That is expected and is the
work that makes the product legitimate. We build it phase by phase, verifying as we go,
exactly as we have so far.
