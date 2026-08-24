# Changelog

All notable changes to kwaro are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- Taint tables for Go, Java, then Solidity AST rules (reentrancy, tx-origin,
  unchecked math) and C/C++ (buffer/integer) via the `kwaro[ast]` extra.
- Model-driven prove step: Ollama/BYOK providers write real PoCs that the
  sandbox executor then runs (offline placeholder stays the default).
- CI/CD guard mode (`--diff` + SARIF to GitHub code scanning).

## [0.7.1] - 2026-08-24

### Fixed
- CLI scan report now shows its work: kept set (or an honest explanation of why
  static-only keeps nothing + how to change it), top 20 ranked findings with
  file:line / rule id / snippet / posterior / CWE, and an evidence trail
  (scan id, files hashed, commit, loop trace, graph validity, sqlite location).
  Previously a scan printed only counts, so findings were invisible.

## [0.7.0] - 2026-08-24

### Added - real analysis depth (`kwaro[ast]` extra)
- Phase 8A: tree-sitter AST layer, `kwaro/ast/parser.py` (lazy per-extension
  parser cache; falls back to regex when the extra is absent - CLI stays zero-dep).
- Rust/Solana rules: missing signer check (CWE-862), missing ownership check
  (CWE-284), unchecked arithmetic (CWE-190). Enabled in the blockchain profile;
  verified on a seeded vulnerable Solana program.
- Phase 8B: intraprocedural taint tracking (`kwaro/ast/taint.py`) for Python and
  JS/TS: untrusted input reaching SQL/shell/eval/DOM sinks, sanitizer-aware
  (int(), parameterized queries, parseInt, encodeURIComponent). Registered as
  analyzer `taint_ast`; enabled in generic + fintech profiles.

### Added - verify loop closes for real
- Phase 8C: sandbox PoC executor (`kwaro scan --execute-pocs`, implies `--pocs`):
  runs generated PoCs in an isolated temp dir with network disabled at the socket
  layer, wall-clock timeout, and output caps. VERIFIED requires exit 0 + explicit
  confirm marker; everything else is UNVERIFIED. A VERIFIED PoC updates the belief
  math (Bayes + SPRT): seeded flows reach posterior 0.635 / SPRT REAL and are kept -
  the first scan where kwaro keeps findings instead of honestly reporting 0.
  Process-level sandbox, not a VM: run untrusted PoCs in a container for
  adversarial targets.

### Changed
- One-env-var BYOK: `kwaro init --provider groq|ollama|auto`; known hosts (groq,
  openai, openrouter, together, deepseek) resolve base URL + API key from their
  standard env vars automatically. Groq default model llama-3.3-70b-versatile.
- README coverage/honesty section updated; docs/coverage.md regenerated from evals.
- Test suite grown from 35 to 52 tests (AST recall, taint recall + FP guards,
  sandbox classification incl. network-block proof).

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
