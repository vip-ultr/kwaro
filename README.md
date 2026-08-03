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

Phases 0-6 are shipped and verified. The CLI stays **zero-dependency** (pure
Python stdlib); the browser UI is an optional `serve` extra (fastapi/uvicorn/websockets).

The core engine, SQLite storage, workspace clone/copy, the math spine (docs/math.md:
Bayesian confidence, loop variant termination, pipeline graph, SPRT stop rule),
providers (Ollama + OpenAI-compatible, offline by default), static analyzers +
domain profiles, the pipeline (L3 ranking, L4 de-dupe, L6 PoC), SARIF/JSON export,
diff-aware rescan (L9), eval (L13), and the browser UI are all implemented and run
end-to-end, with pytest green (35/35).

What works today:

```bash
python3 -m kwaro init                              # detect Ollama, write config (free/offline default)
python3 -m kwaro scan ./my-repo                    # static scan + math spine, math-aware report
python3 -m kwaro scan ./my-repo --profile fintech  # domain-tuned analyzers
python3 -m kwaro scan ./my-repo --rescan          # diff-aware: only changed files (L9)
python3 -m kwaro scan ./my-repo --format sarif    # SARIF 2.1.0 export (math in properties)
python3 -m kwaro scan ./my-repo --format json      # JSON export (L7 + math fields)
python3 -m kwaro chat ./my-repo                    # interactive loop: model uses tools, then reports
```

The static analyzers (secrets, injection, XSS, traversal, auth) are pure-Python,
zero-dep, and CWE-mapped. Domain profiles (generic, fintech, blockchain, ai_app)
select which run. The math spine (docs/math.md) drives confidence, the SPRT stop
rule, the pipeline graph, and loop termination over every finding. Tests assert
recall on a seeded fixture (L13).

`kwaro chat` needs a model. With no model configured it falls back to the
static analyzer; point it at local Ollama (no key) or a hosted BYOK provider.

## Results (eval, L13)

The seeded fixture `tests/fixtures/vuln-repo/` contains one instance of each
detector. `tests/test_eval.py` asserts recall (every seeded rule fires) and flags
unexpected rule ids as possible false positives. Current numbers on the fixture:
100% recall on the 5 seeded rule families (secrets, SQLi, XSS, traversal, auth/md5),
0 unexpected findings. The math spine keeps 0 of 5 static candidates in the
"kept" set because offline static evidence alone does not clear the posterior bar
(0.5) or the SPRT REAL verdict, which is the honest behavior until a PoC verifies.

## Quickstart (once released)

```bash
pip install kwaro            # or: uv tool install kwaro
kwaro init                   # detect Ollama, recommend a local model
kwaro scan ./my-repo         # static-first scan, free, offline
kwaro chat ./my-repo         # conversationally find, prove, fix, verify
```

## Build

Starting implementation? Read [`BUILD.md`](BUILD.md) first. It points to the locked
decisions and the exact next task (Phase 7).

## Docs

All planning, research, and locked decisions are in [`docs/`](docs/). Community
guidelines: [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md),
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

AGPL-3.0. See [LICENSE](LICENSE).
