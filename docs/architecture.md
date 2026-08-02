# kwaro - Architecture

This document is the technical source of truth. It is updated as the build
progresses.

## Overview

kwaro is a single-language (Python 3.10+) application. There is no separate
frontend service, no Postgres, no Docker requirement to run. A scan is executed
as a pipeline of anonymous, provider-attached **steps**, run as jobs, and
surfaced to the user as **scans** and **findings**.

This mirrors the sound parts of open-kritt (anonymous workflow steps executed as
jobs, shown as scans/findings) while being leaner and free-first.

## Components

```
kwaro/
  core/            # shared models, config, storage
    models.py      # Finding, Severity, Scan, StepResult (dataclasses)
    config.py      # load ~/.kwaro/config.toml + env overrides
    storage.py     # SQLite access (one file, zero-config)
    workspace.py   # clone / copy target repo into a temp workspace
  core/providers/  # model provider adapters
    base.py        # Provider interface
    openai_compat.py  # Ollama, Groq, OpenAI, OpenRouter, etc.
    anthropic.py   # Claude (separate format)
  analyzers/       # deterministic static checks (pure Python)
    base.py        # Analyzer interface
    secrets.py, injection.py, xss.py, traversal.py, auth.py
    profiles/      # per-domain rule sets (fintech, blockchain, ai_app)
  chat/            # interactive agent loop (terminal + tool use)
    agent.py       # the loop, step execution, tool dispatch
  ui/              # browser interface (optional extra)
    server.py      # FastAPI app serving the static bundle + WS
    static/        # single static bundle (HTML/CSS/JS)
  tests/           # pytest
```

## Pipeline (a scan)

1. **Workspace**: clone the target (git URL) or copy it (local path) into a
   temp workspace. Diff-aware rescans use git to limit to changed files.
2. **Steps**: the active workflow is a sequence of steps. Each step has:
   - a prompt (focused task, e.g. "find auth bypass in payment paths")
   - a provider/model binding
   - optional attached analyzers (static checks run first)
   - optional a "prover" role (generate a test/PoC for candidates)
3. **Execution**: steps run as jobs. A job invokes the provider (model) with the
   step prompt + workspace context + available tools. Tool calls let the model
   read files, run static analyzers, and request PoC generation.
4. **Aggregation**: results are normalized into `Finding` objects with a
   consistent schema (see core/models.py).
5. **Validation**: de-duplication merges duplicate findings; severity is assigned
   by rankers. A "prover" step generates a failing test or PoC for real
   candidates (the proof layer).
6. **Storage**: findings + scan metadata persist to SQLite.
7. **Presentation**: terminal or browser UI renders scans, findings, PoCs.

## Data model (summary)

- `Finding`: id, scan_id, title, severity (critical/high/medium/low/info),
  file, line, snippet, description, suggested_fix, poc (path or text),
  rule_id/source, confidence.
- `Scan`: id, target, commit, provider, model, created_at, status, finding_count.
- `StepResult`: step id, raw model output, tool calls, extracted findings.

(Exact fields finalized in code; this is the intent.)

## Provider abstraction

A single `Provider` interface: `complete(messages, tools) -> response`.

- `openai_compat.py` covers Ollama (`http://localhost:11434/v1`), Groq,
  OpenAI, OpenRouter, Together, DeepSeek, local llama.cpp, all via the
  OpenAI Chat Completions shape. Config: `base_url`, `api_key`, `model`.
- `anthropic.py` is a thin second adapter for Claude users (different format).
- Default provider: Ollama local. No key, no internet.

Paid providers may block security-research prompts under cyber-safety policies
(open-kritt literally has a `cyber_safety_blocked` failure). Local models do not.
This is why free-default is both cheaper AND more reliable for this job.

## Static analysis

Pure-Python analyzers (regex/AST), zero heavy dependencies in v1:
- secrets (hardcoded keys, tokens)
- injection (SQLi, command injection)
- XSS
- path traversal
- auth gaps (missing checks, weak comparisons)
- per-domain profiles: fintech (PCI/auth), blockchain/Solidity (reentrancy,
  overflow, signature replay, oracle manipulation), AI apps (prompt injection,
  unsafe deserialization of model output).

Static checks run FIRST and reduce false positives; the model then triages and
explains only real candidates.

## PoC / test generation (the differentiator)

A step may include a "prover" instruction: for each candidate finding, ask the
model to generate a minimal failing test or PoC. v1 generates the test/PoC file.
Execution is behind an opt-in, sandboxed flag (run in a temp dir, no network,
no writes outside the sandbox) and is OFF by default.

## Storage

SQLite, one file (`~/.kwaro/kwaro.db`), zero config, cross-OS. No server, no
migrations framework. Schema is additive and versioned in code.

## Interfaces

- Terminal: `kwaro chat` (interactive loop) and `kwaro scan <path|url>`.
- Browser: `kwaro serve` (FastAPI + single static bundle). Dark, sharp UI using
  the locked palette (docs/brand.md). Optional dependency group `serve`.
- Both drive the same engine and read the same SQLite store.

## Cross-OS

Pure stdlib, `pathlib` for paths, `subprocess` with list args. No compiled
extensions, no Docker. Runs on Windows, macOS, Linux, WSL.
