# kwaro - Roadmap

Phased build. Each phase ends in something runnable and verified.

## Phase 0 - Scaffold (DONE)
- Repo, folder structure, LICENSE (AGPL-3.0), brand palette, logo, docs skeleton.
- `python -m kwaro` runs. Zero runtime deps.

## Phase 1 - Core engine + math spine (DONE, 2026-08-03)
- `core/models.py` (Finding, Scan with L7 + math fields), `core/storage.py`
  (SQLite, persists math fields), `core/workspace.py` (clone/copy + hashing).
- Math spine (docs/math.md): `core/verify.py` (Bayesian update + SPRT),
  `core/graph.py` (FIND/PROVE/FIX/VERIFY/DONE state machine + trace validator),
  `core/loop.py` (bounded loop with variant termination).
- `kwaro init` writes `~/.kwaro/config.toml`; `kwaro scan <path|url>` runs the
  analyzer + math spine end to end and prints a math-aware report.
- Verify: `kwaro scan tests/fixtures/vuln-repo` finds secret + SQLi, runs the
  loop, validates the pipeline graph, persists findings to SQLite. pytest: 4/4.
- Note: `core/config.py` was folded into `kwaro init` + providers (Phase 2); the
  schema lives in L7, not a separate module yet.

## Phase 2 - Providers
- `openai_compat.py` (Ollama/Groq/OpenAI/...), `anthropic.py`.
- `kwaro chat` loop with tool dispatch.
- Verify: chat works against local Ollama; falls back to rule-based without a model.

## Phase 3 - Static analyzers
- secrets, injection, xss, traversal, auth (pure Python).
- Per-domain profiles (fintech, blockchain, ai_app).
- Verify: analyzers flag a deliberately vulnerable fixture repo.

## Phase 4 - Pipeline + proof
- Step runner, job execution, aggregation, de-dupe, severity rankers.
- "prover" step: generate test/PoC for candidates (v1: generate-only).
- Verify: end-to-end scan of fixture produces ranked, de-duped findings + PoCs.

## Phase 5 - CLI polish
- `kwaro scan`, SARIF/JSON export, diff-aware rescan.
- Verify: export valid SARIF; rescan only changed files.

## Phase 6 - Browser UI
- `kwaro serve`: FastAPI + static bundle, finding cards, live activity, chat panel.
- Verify: UI shows a scan; chat drives a scan.

## Phase 7 - Docs, tests, release
- README with screenshots, CONTRIBUTING, full pytest suite, package on PyPI.
- Verify: `pip install kwaro` works on a clean machine (Linux/macOS/Windows).

## Principles throughout
- Free-first, local-first, cross-OS, zero runtime deps.
- Proof over assertion (PoC/test generation).
- Update these docs as decisions change.
