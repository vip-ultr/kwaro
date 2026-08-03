# Changelog

All notable changes to kwaro are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned (see docs/roadmap.md)
- Providers: Ollama + OpenAI-compatible adapter (Phase 2)
- Static analyzers + generic profile (Phase 3)
- Pipeline + PoC generate-only (Phase 4)
- CLI: scan, SARIF/JSON export, diff-aware rescan (Phase 5)
- Browser UI: serve + finding cards + live activity (Phase 6)
- Docs, tests, PyPI release (Phase 7)

### Added (scaffold)
- Repository, folder structure, AGPL-3.0 license.
- Brand: palette + aperture chevron logo.
- Full planning set: vision, architecture, providers, agents, UI, roadmap.
- Research: feasibility (research.md), resolved gaps (decisions-unlocked.md),
  locked decisions (locked-decisions.md), game-changers.
- Community docs: CONTRIBUTING, SECURITY, CODE_OF_CONDUCT.
- Specs: domain profiles (profiles.md), fail states (fail-states.md),
  release process (release.md).

## [0.6.0] - 2026-08-03
- Phase 6 browser UI: `kwaro/web/static/` hand-written bundle (no React build, L11)
  with finding cards that expose the math (posterior, SPRT verdict, composite
  confidence, PoC state); activity + chat panels.
- `kwaro/serve.py` - FastAPI app (lazy import so the CLI stays zero-dep, L1): serves
  the bundle, `POST /api/scan` (runs the real pipeline, returns findings w/ math),
  `POST /api/chat`, `WS /ws/activity`. `kwaro serve [--port 8080]`.
- `pyproject.toml` `serve` extra = fastapi, uvicorn, websockets (optional).
- Tests: 5 serve tests via FastClient (index, static, scan runs pipeline + returns
  math, SARIF export, chat reply). Full suite 35/35 pass. CLI runs with extra absent.
- CI: `.github/workflows/ci.yml` runs pytest on ubuntu/macos/windows x Python 3.10-3.12,
  installing `.[dev,serve]`. Packaging verified: `uv build` produces a pure-Python wheel
  with zero runtime deps (only `dev`/`serve` extras). First release: v0.6.0.

## [0.5.0] - 2026-08-03
- Phase 5 CLI polish: `core/export.py` (SARIF 2.1.0 + JSON carrying L7 fields + math
  under properties/summary); `kwaro scan --format sarif|json`.
- L9 diff-aware rescan: `core/storage.py` baseline table (target+profile -> commit +
  file hashes); `core/workspace.py` relative-path indexing + `diff_targets()` (git
  commit diff or local hash diff). `kwaro scan --rescan` scans only changed files.
- Eval (L13): `tests/test_eval.py` asserts recall on the seeded fixture and flags
  unexpected rule ids as possible FPs. Full suite 30/30 pass. Zero new runtime deps.

## [0.4.0] - 2026-08-03
- Phase 4 pipeline + proof: `core/rank.py` (L3 severity bands + composite confidence,
  L4 root-cause fingerprint + de-dupe), `core/pipeline.py` (FIND/PROVE/FIX/VERIFY
  stages orchestrating the math spine, then aggregate -> de-dupe -> rank),
  `analyzers/prover.py` (PoC generate-only, L6: never executes offline).
- `kwaro scan --pocs` generates per-finding PoC placeholders; `--profile` selects
  analyzers. `Scan.kept_count` added and persisted (L8).
- Tests: Phase 4 suite (rank bands, composite confidence, L4 dedup, prover offline,
  pipeline end-to-end). Full suite 23/23 pass. Zero new runtime deps.

## [0.3.0] - 2026-08-03
- Phase 3 static analyzers: `kwaro/analyzers/base.py` (Analyzer/Rule/REGISTRY),
  `secrets.py`, `injection.py`, `xss.py`, `traversal.py`, `auth.py` (pure-Python,
  CWE-mapped rule sets). XSS is extension-gated to web languages.
- `kwaro/core/profiles.py` + `core/profiles/*.toml`: generic, fintech, blockchain,
  ai_app. `kwaro scan --profile <name>` selects analyzers.
- `kwaro scan` routed through the analyzer registry; Phase 1 math spine intact.
- Tests: Phase 3 suite (5 analyzers + profile filtering) on a multi-lang fixture.
  Full suite 16/16 pass. Zero new runtime deps.

## [0.2.0] - 2026-08-03
- Phase 2 providers: `core/config.py` (zero-dep TOML config), `core/providers/base.py`
  (Provider interface + message/tool types), `core/providers/openai_compat.py`
  (Ollama/Groq/OpenAI/OpenRouter over stdlib urllib, no requests dep),
  `core/providers/anthropic.py` (thin second adapter), `core/providers/__init__.py`
  (factory from config).
- `kwaro/chat/agent.py`: interactive loop with governed tool registry (read_file,
  run_analyzer, request_poc, done), stop condition + iteration cap. Anonymous steps.
- `kwaro chat <path|url>` wired into CLI; `kwaro init` uses Config.
- Tests: Phase 2 suite (config round-trip, factory, chat loop with fake provider).
  Full suite 9/9 pass. Zero new runtime deps.

## [0.1.0] - 2026-08-03
- Phase 1 core engine: `core/models.py` (Finding/Scan with L7 + math fields),
  `core/storage.py` (SQLite persisting math fields), `core/workspace.py`
  (clone/copy + file hashing).
- Math spine (docs/math.md): `core/verify.py` (Bayesian confidence + SPRT stop
  rule), `core/graph.py` (FIND/PROVE/FIX/VERIFY/DONE state machine + trace
  validator), `core/loop.py` (bounded loop with variant termination).
- `kwaro init` and `kwaro scan <path|url>` wired to the math spine; minimal
  static analyzer (secret + SQLi) so the loop has real findings.
- Tests: fixture vuln repo + pytest smoke test (4/4 pass). Zero new runtime deps.

## [0.0.0] - 2026-08-02
- Project inception and planning.
