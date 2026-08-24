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

## Where to start: Phases 8 A-D are ALL SHIPPED - next is language rollout (Go, Java, Solidity, C/C++)

Phase 8 core shipped 2026-08-24 (commits 04b16d8..HEAD), suite 52/52 green:
- Phase A: kwaro/ast/parser.py + rules/rust_solana.py (signer CWE-862 / ownership
  CWE-284 / unchecked arith CWE-190); fixture tests/fixtures/rust-solana/;
  tests/test_phase8.py.
- Phase B: kwaro/ast/taint.py intraprocedural taint (Python + JS tables),
  registered as analyzer 'taint_ast' in generic/fintech profiles; fixtures
  py-web + js-web; tests/test_phase8b.py (recall + sanitizer FP guards).
- Phase C: analyzers/sandbox.py - opt-in PoC execution (`--execute-pocs`): no
  network (sockets blocked), timeout, VERIFIED only on KWaro_POC_CONFIRMED +
  exit 0. Verified end to end: confirming PoCs move posterior to 0.635 /
  SPRT REAL -> kept=3 on the py fixture (first scan that KEEPS findings).
  tests/test_phase8c.py.
- Phase D: docs/coverage.md rewritten from the evals; README honesty section
  updated (ast+taint shipped, sandbox shipped, intraprocedural-only scope).

Phases 0-7 are DONE and verified (commits in git history) and kwaro is published to
PyPI/Homebrew/Scoop. Do NOT rebuild the existing engine (core/, providers, analyzers/
regex layer, chat, web, serve, packaging).

NEXT WORK (in order):
1. Extend taint LANGS tables to Go, then Java (grammar already in `ast` extra);
   seed fixtures go-svc/, java-svc/; eval per language before claiming it.
2. Solidity AST rules (reentrancy, tx-origin, unchecked math) via
   tree-sitter-solidity (community grammar).
3. Model-driven prove step: wire providers into generate_poc so Ollama/BYOK can
   write real PoCs that the sandbox then executes (offline placeholder stays default).
4. CI/CD guard mode (`--diff` + SARIF to code scanning) still marked planned in README.

Honesty rules carried from the plan: no language claimed until its eval passes; we do not
claim to beat CodeQL; regex stays the zero-dep default; `ast` is opt-in depth only;
taint is intraprocedural only; sandbox is process-level, not a VM.

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
