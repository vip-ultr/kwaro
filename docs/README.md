# kwaro Documentation

> **New here / new session?** Start with [`BUILD.md`](../BUILD.md) (repo root). It
> points to the locked decisions and the exact next task (Phase 1).

This folder is the source of truth for kwaro's plan, architecture, and decisions.
Everything is documented here before implementation, so the project stays coherent
as it grows.

## Start here

- `vision.md` — what kwaro is, who it's for, the principles.
- `architecture.md` — how the pieces fit (engine, providers, analyzers, UI).
- `game-changers.md` — the differentiators that make kwaro "mind-blowing".

## Engineering & decisions

- `locked-decisions.md` — **14 final, non-negotiable design choices (L1-L14).** Build against this.
- `research.md` — feasibility research + verified gaps (G1-G6).
- `decisions-unlocked.md` — research on areas initially open (U1-U9), now resolved.
- `agents.md` — why agents are anonymous steps, not named personas (option A).
- `providers.md` — model provider strategy (free-first, bring-your-own-key).
- `ui.md` — terminal + browser UI direction.
- `math.md` — the locked math primitives (Bayesian confidence, loop variant, pipeline graph) with verified examples.
- `profiles.md` — domain profile format + discovery (the community growth loop).
- `fail-states.md` — first-run flow + every failure state, stated honestly.
- `release.md` — versioning, changelog, PyPI, cross-OS CI.
- `roadmap.md` — phased build plan.
- `brand.md` — palette + logo.
- `content.md` — voice, UI strings, finding/chat copy, error text, launch post.

## Community

- `CONTRIBUTING.md` (repo root) — how to contribute, DCO sign-off, dev setup.
- `SECURITY.md` (repo root) — threat model, privacy posture, vulnerability reporting.
- `CODE_OF_CONDUCT.md` (repo root) — Contributor Covenant v2.1.

## How to read this

Start with `vision.md` and `game-changers.md` for the "why", then
`locked-decisions.md` for the "what we build", then `roadmap.md` for the "when".
Each document is a living plan: update it as decisions change.
