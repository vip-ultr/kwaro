# kwaro - Agents (anonymous steps)

Per the decided direction (option A), kwaro does NOT use named agent personas in
the core. Agents are anonymous, provider-attached **workflow steps** executed as
jobs, surfaced to the user as scans and findings. This matches the sound
architecture of open-kritt while staying lean and free-first.

This keeps the project open-source-clean: no cultural lock-in, no hardcoded
personalities, and the roster is data, not code.

## What a "step" is

A step is the unit of work in a workflow. It has:

- `prompt`: a focused task (e.g. "find auth bypass in payment paths").
- `provider` / `model`: which model runs it (provider-attached, not named).
- `analyzers`: optional static checks run first (deterministic pre-filter).
- `prover`: optional flag to generate a test/PoC for candidate findings.
- `tools`: what the model may call (read file, run analyzer, request PoC).

## Pipeline roles (internal, not user-facing names)

These are pipeline STAGES, not personas. They may appear in logs as stage labels
("analyze", "prove", "rank") but are not branded agents:

1. **recon** - clone/copy target, enumerate files, build attack surface.
2. **analyze** - static analyzers + model triage of candidate findings.
3. **prove** - generate a failing test / PoC for real candidates.
4. **rank** - de-duplicate, assign severity, mark false positives.
5. **report** - write findings, SARIF/JSON, explanations.

## Why no named agents

- open-kritt, a serious security product, uses unnamed steps and it works.
- Named personas add UX polish but also brand/cultural lock-in and complexity.
- The engine stays clean and contributable; anyone can add a step type via config
  or a PR without adopting our creative naming.

## Future option (not v1)

A thin, optional UX layer could attach friendly labels to stages, fully
configurable via an `agents` manifest and OFF by default. This is deferred until
the core proves out. If added later, names must remain overridable defaults.
