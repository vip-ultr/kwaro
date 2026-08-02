# kwaro

**A free, open-source security scanner for every developer, on every OS.**

kwaro helps you find real vulnerabilities in your code by chatting with a local AI
agent, no paid APIs required, no Docker stacks, no lock-in. It runs anywhere:
Windows, macOS, Linux, and WSL.

> This repository is in active planning + build. Architecture, plans, and design
> decisions live in [`docs/`](docs/). The plan is fully specified; implementation
> follows it phase by phase.

## Why kwaro

- **100% free by default.** Runs on a local model via Ollama. No credit card, no
  account, fully offline. Paid models (OpenAI, Groq, OpenRouter, etc.) are opt-in
  through a standard OpenAI-compatible API.
- **Local-first privacy.** Your code never leaves your machine. Ever. A real
  advantage for fintech, banking, and blockchain teams blocked from cloud scanners.
- **Cross-platform.** Pure-Python, zero native dependencies. One codebase runs on
  Windows, macOS, Linux, and WSL.
- **Proof, not opinion.** Findings can be proven with a generated, runnable
  proof-of-concept (PoC), then fixed and verified, in one local session.
- **Any codebase, any domain.** Generic scanning plus community domain profiles
  (fintech, blockchain, AI apps).
- **Two interfaces, one engine.** Talk to it in your terminal (`kwaro chat`) or in a
  modern browser UI (`kwaro serve`). Same agent, same findings.
- **Open source, AGPL-3.0.** Free for everyone, forever. Forkers must stay open.

## The loop that makes it different

`Find -> Prove -> Fix -> Verify`, all on your machine, for free:

1. **Find** via static analyzers + model triage.
2. **Prove** by generating and running a PoC that shows the actual crash.
3. **Fix** via the chat agent that edits the file.
4. **Verify** by re-scanning to confirm the bug is gone.

See [`docs/game-changers.md`](docs/game-changers.md) for the full differentiation
story, and [`docs/locked-decisions.md`](docs/locked-decisions.md) for the locked
engineering decisions.

## Status

Active build. See [`docs/roadmap.md`](docs/roadmap.md). Early phases: core engine,
providers, static analyzers, pipeline + PoC, CLI + SARIF, then the browser UI.

## Quickstart (once released)

```bash
pip install kwaro            # or: uv tool install kwaro
kwaro init                   # detect Ollama, recommend a local model
kwaro scan ./my-repo         # static-first scan, free, offline
kwaro chat ./my-repo         # conversationally find, prove, fix, verify
```

## Docs

All planning, research, and locked decisions are in [`docs/`](docs/). Community
guidelines: [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md),
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

AGPL-3.0. See [LICENSE](LICENSE).
