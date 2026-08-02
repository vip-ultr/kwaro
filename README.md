# kwaro

**A free, open-source security scanner for every developer, on every OS.**

kwaro is a worldwide, community-driven project. It helps you find
real vulnerabilities in your code by chatting with a local AI agent, no paid APIs
required, no Docker stacks, no lock-in. It runs anywhere: Windows, macOS, Linux, and
WSL.

> This repository is in early scaffolding. Architecture, plans, and design decisions
> live in [`docs/`](docs/). Implementation follows the plan.

## Why kwaro

- **100% free by default.** Runs on a local model via Ollama. No credit card, no
  account, fully offline. Paid models (OpenAI, Groq, OpenRouter, etc.) are opt-in
  through a standard OpenAI-compatible API.
- **Cross-platform.** Pure-Python, zero native dependencies. One codebase runs on
  Windows, macOS, Linux, and WSL.
- **Two interfaces, one engine.** Talk to it in your terminal (`kwaro chat`) or in a
  modern browser UI (`kwaro serve`). Same agent, same findings.
- **Open source, AGPL-3.0.** Free for everyone, forever.

## Status

Scaffolding phase. See [`docs/`](docs/) for the plan and decisions.

## License

AGPL-3.0. See [LICENSE](LICENSE).
