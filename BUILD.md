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

## Where to start: Phase 8 - real multi-language depth (Phases 0-7 shipped)

Phases 0-7 are DONE and verified (commits in git history) and kwaro is published to
PyPI/Homebrew/Scoop. Do NOT rebuild the existing engine (core/, providers, analyzers/
regex layer, chat, web, serve, packaging). The gap is ANALYSIS DEPTH: today's 5 regex
rules return 0 on a Rust/Solana repo because they don't cover those vuln classes.
Start here:

Goal (Phase 8): make kwaro credible on "any codebase" via tree-sitter AST + intra
procedural taint (the `kwaro[ast]` extra), honest about the Semgrep-CE-class target.
Full plan and architecture: `docs/plan-phase8.md`. Resume from there.

Concrete tasks (in order; each ends runnable + verified on a seeded fixture):
1. `kwaro/ast/parser.py` - lazy tree-sitter Parser cache per extension; falls back to
   regex when the extra is absent. Add `ast` extra to pyproject (tree-sitter + grammars).
2. `kwaro/ast/queries/` - Rust `.scm` queries for: missing signer check, missing ownership
   check, unchecked arithmetic (overflow), account confusion.
3. `kwaro/ast/rules/` - Rust/Solana rule defs consuming those queries; integrate into the
   analyzer registry (regex mode OR ast mode, chosen at runtime).
4. `tests/fixtures/rust-solana/` - seeded Solana program with one instance of each rule.
   `tests/test_eval.py` asserts 100% recall on it (L13). This is the bar Rust is "done".
5. Then Phase B (taint.py), Phase C (real PoC per L6), Phase D (docs/coverage.md matrix).

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
