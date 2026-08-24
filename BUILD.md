# Build Guide (start here in a new session)

This file lets a fresh session start building without re-reading every doc. It
points to the locked decisions and the next concrete task.

## What kwaro is (one paragraph)

A free, open-source, local-first security scanner. It scans any codebase with a
local AI model (Ollama, offline, free), finds vulnerabilities via static analyzers
+ model triage, PROVES them with a generated/runnable PoC, then helps fix and
verify, all on the user's machine. Two interfaces on one Python engine: terminal
(`kwaro chat` / `kwaro scan`) and browser (`kwaro serve`). AGPL-3.0.

## Hard constraints (never violate these)

1. **Zero runtime dependencies for the CLI.** Pure Python stdlib only in `kwaro/`.
   `serve` extra may add fastapi/uvicorn/websockets. `dev` adds pytest. Nothing else.
2. **Single language:** Python 3.10+. No Node, no React, no Docker required to run.
3. **Local-first / private:** default provider is Ollama, offline, no key, no
   telemetry, no network for analysis.
4. **No competitor names anywhere in the product** (user rule).
5. **Agents are anonymous workflow steps, not named personas** (option A).
6. **Honest about confidence:** static / model / verified are distinct states. An
   UNVERIFIED PoC never raises severity. Never imply proof that didn't happen.

## Locked decisions to build against

Read `docs/locked-decisions.md` (L1-L14). The ones that shape Phase 1 most:
- L1 free-first/local-first/zero-dep runtime
- L5 deterministic tool-call validation (validator + retry + fallback)
- L7 exact data model (Finding / Scan / StepResult fields)
- L8 SQLite, one file, zero-config (`~/.kwaro/kwaro.db`)
- L9 diff-aware rescan (git diff baseline / file-hash baseline)
- L12 first-run `kwaro init` + static-only fallback

## Where to start: Phase 8 Phase A is SHIPPED - resume at Phase B (taint)

Phase A (Rust/Solana AST depth) shipped and verified (2026-08-24 session):
`kwaro/ast/` exists (parser.py lazy tree-sitter cache + rules/rust_solana.py with
missing-signer, missing-ownership, unchecked-arithmetic). Seeded fixture at
tests/fixtures/rust-solana/programs/vault/src/lib.rs; tests/test_phase8.py asserts
recall + FP guard; suite 40/40 green; `kwaro scan --profile blockchain` returns real
findings on the fixture. Without the `ast` extra the analyzer returns [] cleanly
(verified by blocking tree_sitter imports) - zero-dep CLI intact.

Phases 0-7 are DONE and verified (commits in git history) and kwaro is published to
PyPI/Homebrew/Scoop. Do NOT rebuild the existing engine (core/, providers, analyzers/
regex layer, chat, web, serve, packaging).

Next: Phase B of docs/plan-phase8.md - intraprocedural taint (`kwaro/ast/taint.py`),
then Phase C (real PoC execution per L6), Phase D (coverage matrix per-language eval).
Language order after Rust: Python/JS -> Go -> Java -> Solidity -> C/C++/PHP.

Honesty rules carried from the plan: no language claimed until its eval passes; we do not
claim to beat CodeQL; regex stays the zero-dep default; `ast` is opt-in depth only.

Existing verified behavior to preserve (do not regress):
- `kwaro scan <git-url|path>` clones/copies, records a Scan row, runs the math spine end
  to end; SQLite stores findings + math fields (prior, posterior, evidence, sprt_decision,
  stage, loop_variant). `pytest` is green (35/35) and CI runs the matrix. Keep it green.
- CLI stays zero-dependency; `serve` and now `ast` are optional extras.

## Reading order for a new session

1. This file (BUILD.md)
2. docs/locked-decisions.md (the rules)
3. docs/roadmap.md (the phases)
4. docs/architecture.md (the shape)
5. docs/content.md (the strings to use)
Then build Phase 1.

## Verification habit

After each phase: run the code for real (not just import), run `pytest`, confirm
zero new runtime deps (`pip check` / inspect imports). Report actual output, not
intent.
