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
