# kwaro - Vision

kwaro is a free, open-source security scanner for every developer, on every OS.
It helps you find real vulnerabilities in code by chatting with a local AI agent,
no paid APIs required, no Docker stacks, no lock-in.

## Positioning

kwaro is a worldwide, community-driven project. The name stands on its own; the
project is for everyone, regardless of region.

We are building something that beats heavy, paid, localhost-only scanners
(notably open-kritt) on the things that matter:

- **100% free by default.** Runs on a local model via Ollama. No credit card, no
  account, fully offline. Paid models (OpenAI, Groq, OpenRouter, etc.) are opt-in
  through a standard OpenAI-compatible API.
- **Cross-platform.** Pure-Python, zero native dependencies. One codebase runs on
  Windows, macOS, Linux, and WSL.
- **One language, lean infra.** No polyglot stack (open-kritt uses React + Node +
  Prisma + Postgres + a Python engine + Docker). kwaro is Python only, SQLite only,
  no Docker required to run.
- **Proof, not opinion.** Findings are backed by a generated test or proof-of-concept
  (PoC) where possible, not just a model's guess. This is our core differentiator.
- **Two interfaces, one engine.** Terminal chat (`kwaro chat`) and a browser UI
  (`kwaro serve`) both drive the same engine.

## Who it is for

- Security researchers and security-minded developers who want control over their
  prompts, workflows, model providers, and infrastructure.
- Anyone who wants to scan a repo without paying per scan or sending code to a
  third party.

## What it scans

kwaro scans any codebase, any language, any domain. The generic engine catches
common and critical vulnerability classes everywhere. For expert-level results in
specific domains, we ship per-domain scan profiles (fintech, blockchain/Solidity,
AI apps). See architecture.md.

## Principles

1. Free-first. The default experience costs nothing and needs no account.
2. Local-first. Your code stays on your machine. No mandatory network calls.
3. Open source, AGPL-3.0. Free for everyone, forever.
4. Honest about limits. We claim "works on any code, gets smarter per domain,"
   not "finds everything perfectly."
5. Proof over assertion. A finding is stronger when we can show the crash.
