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

## Phase 2 - Providers + chat loop (DONE, 2026-08-03)
- `core/config.py`: loads/saves `~/.kwaro/config.toml` (minimal zero-dep TOML
  parser, works on Python 3.10+ without tomllib).
- `core/providers/base.py`: Provider interface + Message/ToolCall/ToolSpec/Response.
- `core/providers/openai_compat.py`: Ollama/Groq/OpenAI/OpenRouter/... over stdlib
  `urllib` (no requests dep). Local Ollama needs no key.
- `core/providers/anthropic.py`: thin second adapter, different request/response shape.
- `core/providers/__init__.py`: factory picks adapter from config.
- `kwaro/chat/agent.py`: interactive loop with a governed tool registry (read_file,
  run_analyzer, request_poc, done) and a stop condition (no tool calls) + iteration
  cap. Tools are anonymous steps (L14), not named personas.
- `kwaro chat <path|url>` wired into the CLI; `kwaro init` uses Config.
- Verify: pytest 9/9 (config round-trip, factory, chat loop with a fake provider
  exercising tool dispatch + stop + cap). `kwaro init` writes a config that reloads
  and builds a provider. No live model needed for tests.

## Phase 3 - Static analyzers (DONE, 2026-08-03)
- `kwaro/analyzers/base.py`: Analyzer interface + Rule + REGISTRY + scan_file().
- `kwaro/analyzers/secrets.py`, `injection.py`, `xss.py`, `traversal.py`, `auth.py`:
  pure-Python rule sets returning Finding objects (CWE-mapped). XSS is
  extension-gated to web languages; secrets catches AWS keys + private-key blocks.
- `kwaro/analyzers/__init__.py`: imports populate REGISTRY.
- `kwaro/core/profiles.py` + `kwaro/core/profiles/*.toml`: generic, fintech,
  blockchain, ai_app. Profile selects which analyzers run (docs/profiles.md).
- `kwaro scan <path|url> [--profile fintech]` wired through the analyzer registry;
  the Phase 1 math spine (prove/fix/verify) still runs over the findings.
- Verify: pytest 16/16 (5 analyzers + profile filtering) on a multi-lang fixture.
  Generic scan finds 5 candidates; fintech profile runs 4 (xss off) and finds 4.

## Phase 4 - Pipeline + proof
- Step runner, job execution, aggregation, de-dupe (L4), severity rankers (L3).
- "prover" step: generate test/PoC for candidates (v1: generate-only, sandbox off).
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
