# Security Policy

kwaro is a local security scanner. This document states what it does, what it
cannot do, and how to report problems. Read it before running scans or PoC
execution.

## Threat model

**What kwaro is for**
- Finding vulnerabilities in code you own or are authorized to test.
- Running entirely on your machine by default.

**What leaves your machine (default configuration)**
- Nothing. With the default local provider (Ollama), analysis is fully offline.
  No code, snippets, or findings are uploaded anywhere.
- The only network traffic is what YOU opt into:
  - A non-local provider (Groq/OpenAI/OpenRouter/...). Then prompts + context go to
    that provider per their terms.
  - `kwaro update` or explicit version checks (off by default).
- There is **no telemetry, no crash reporting, no analytics** in kwaro.

**PoC execution (opt-in, not default)**
- `kwaro prove <id>` / `--execute-poc` runs generated code. This is OFF by default.
- When enabled, it runs in a separate process with: a temp working directory only,
  no network (best-effort), CPU/time/memory limits, and is killed on breach.
- This is a **soft boundary, not a hard security sandbox**. Generated code may be
  malicious or buggy. Run untrusted PoCs in a container or virtual machine you can
  discard.
- A VERIFIED PoC means it reproduced the expected failure in that sandbox; it does
  NOT mean the sandbox is safe against a determined attacker.

**What kwaro cannot guarantee**
- It will not find every vulnerability. It complements, not replaces, expert review
  and mature SAST tools.
- Model output can be wrong. Findings tagged `model-only` or `unverified` are
  lower-confidence by design (see docs/locked-decisions.md L3/L6).

## Authorized use only

Only scan code you are authorized to test. kwaro must not be used for unauthorized
access or attacks against systems you do not own.

## Reporting a vulnerability in kwaro itself

If you find a security flaw in kwaro (not in scanned code), report it privately:

- Open a GitHub Security Advisory (preferred), or
- Email the maintainers (see profile) with "kwaro security" in the subject.

Do not open a public Issue for kwaro's own vulnerabilities. We will acknowledge
within 5 business days and coordinate a fix.

## Supply chain

- Runtime has zero third-party dependencies. The only added deps are the optional
  `serve` extra (fastapi, uvicorn, websockets) and `dev` (pytest). Review
  `pyproject.toml`.
- We do not execute arbitrary install scripts. Install via `pip`/`uv` from the repo
  or PyPI.
