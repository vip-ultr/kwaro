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

## Where to start: Phase 1

Goal: a runnable core that can clone/copy a target, store scans, and define the
data model, with the tool-call validation scaffold, with ZERO new runtime deps.

Concrete tasks (in `kwaro/`):
1. `core/config.py` - load `~/.kwaro/config.toml` + env overrides; `kwaro init`
   detects Ollama, recommends a 14B model, writes config. See docs/providers.md,
   docs/fail-states.md (first-run copy), docs/content.md (strings).
2. `core/models.py` - dataclasses for Finding / Scan / StepResult per L7.
3. `core/storage.py` - SQLite open/create/migrate; insert scan + findings.
4. `core/workspace.py` - clone git URL OR copy local path into a temp workspace;
   compute file hashes for diff-aware rescan (L9).
5. `core/providers/tools.py` - tool schema definitions + a validator that checks
   name known / args parse / required present; retry-with-correction + static-only
   fallback (L5). This is the foundation the agent loop (Phase 2) uses.
6. `cli.py` / `__main__.py` - `kwaro init`, `kwaro scan <path|url>` (static-only for
   now), `kwaro chat` (stub that explains static-only until Phase 2).

Definition of done for Phase 1:
- `kwaro init` works and writes config.
- `kwaro scan ./some-repo` clones/copies, records a Scan row, finds NOTHING yet
  (analyzers are Phase 3) but runs end-to-end without error.
- `kwaro scan <git-url>` clones and scans.
- SQLite has the scan + (later) findings.
- `python -m kwaro` and `kwaro` (after install) both run. Zero new runtime deps.
- A pytest smoke test confirms the above on a tiny fixture (add `tests/fixtures/`).

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
