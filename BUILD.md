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

## Where to start: Phase 4 (Phases 0-3 shipped)

Phases 0, 1, 2, and 3 are DONE and verified (commits in git history). Do NOT
rebuild core/ (models, storage, workspace, verify, graph, loop, config, profiles),
the providers stack, kwaro/chat/agent.py, or kwaro/analyzers/. Start here:

Goal (Phase 4): the step runner + pipeline that aggregates findings, de-dupes by
root cause (L4), assigns severity (L3), and generates a PoC for candidates
(v1: generate-only, sandbox off by default, L6). Zero new runtime deps.

Concrete tasks (in `kwaro/`):
1. `core/pipeline.py` - run the FIND/PROVE/FIX/VERIFY stages as explicit steps,
   aggregate Finding objects, de-dupe by fingerprint (L4).
2. `core/rank.py` - composite confidence + severity bands (L3), mark false positives.
3. `analyzers/prover.py` - generate a minimal failing test/PoC file for a candidate
   (model-driven when a provider is configured; offline placeholder otherwise).
4. `core/__main__.py` scan path - call the pipeline instead of the inline loop.run,
   keep the math spine (verify/bayes/sprt/graph) intact.
6. `cli.py` / `__main__.py` - `kwaro init`, `kwaro scan <path|url>` (static-only for
   now), `kwaro chat` (stub that explains static-only until Phase 2).

Definition of done for Phase 1 (SHIPPED 2026-08-03):
- `kwaro init` works and writes config.
- `kwaro scan ./some-repo` clones/copies, records a Scan row, runs the math spine
  end to end. A minimal static analyzer (secret + SQLi regex) is in place so the
  loop has real findings to prove/verify; full per-language analyzers are Phase 3.
- `kwaro scan <git-url>` clones and scans.
- SQLite has the scan + findings, including the math fields (prior, posterior,
  evidence, sprt_decision, stage, loop_variant).
- `python -m kwaro` and `kwaro` (after install) both run. Zero new runtime deps.
- A pytest smoke test confirms the above on a tiny fixture (tests/fixtures/).

NOTE FOR A FRESH SESSION: Phase 1 is complete. Do NOT rebuild models/storage/
workspace/verify/graph/loop. Start at Phase 2 (providers + `kwaro chat` loop).

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
