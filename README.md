# kwaro

<p align="center">
  <strong>A free, open-source security scanner that finds, proves, fixes, and verifies vulnerabilities on your machine.</strong>
</p>

<p align="center">
  <img alt="License: AGPL-3.0" src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" />
  <img alt="Python: 3.10-3.12" src="https://img.shields.io/badge/python-3.10--3.12-blue.svg" />
  <img alt="Runtime deps: zero" src="https://img.shields.io/badge/runtime%20deps-zero-brightgreen.svg" />
  <img alt="CI: pytest matrix" src="https://img.shields.io/badge/CI-pytest%20%7C%20linux%2Fmac%2Fwin-blue.svg" />
  <img alt="Platform: cross-OS" src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20WSL-lightgrey.svg" />
</p>

<p align="center">
  <code>pip install kwaro</code> &nbsp;·&nbsp; runs on a local model (Ollama) with no API key and no internet, ever.
</p>

---

kwaro helps you find real vulnerabilities in your code by chatting with a local AI
agent. No paid APIs, no Docker stacks, no lock-in. It runs anywhere: Windows, macOS,
Linux, and WSL.

Most scanners stop at "here is a bug." kwaro goes further, all locally, all for free:
it **finds** a vulnerability, **proves** it with a runnable proof-of-concept, **fixes**
it with a codebase-aware patch, and **verifies** the fix by re-scanning. You watch a
finding go from "reported" to "proven" to "fixed and verified" in one session, on your
own hardware.

> kwaro is fully built and released (v0.6.0). Architecture, research, and all design
> decisions live in [`docs/`](docs/). This README is the user-facing entry point.

## Why kwaro

- **100% free by default.** Runs on a local model via Ollama. No credit card, no
  account, fully offline. Paid models (OpenAI, Groq, OpenRouter, and any
  OpenAI-compatible API) are opt-in via bring-your-own-key.
- **Privacy as a feature, not a footnote.** Your code never leaves your machine. With
  the default local provider, analysis is fully offline. There is no telemetry, no
  crash reporting, no analytics. This is a hard requirement for fintech, banking, and
  blockchain teams blocked from cloud scanners.
- **Cross-platform, zero runtime dependencies.** Pure Python 3.10+, standard library
  only for the CLI. One codebase on Windows, macOS, Linux, and WSL.
- **Proof, not opinion.** Every finding shows its evidence chain: static rule hit?
  model confirmation? PoC verified? Confidence is derived from the loop, not asserted
  by the model.
- **Any codebase, any domain.** Generic scanning plus community domain profiles
  (fintech, blockchain, AI apps). Profiles are plain files anyone can write and submit.
- **Two interfaces, one engine.** Talk to it in your terminal (`kwaro chat`) or in a
  browser UI (`kwaro serve`). Same agent, same findings.
- **Open source, AGPL-3.0.** Free for everyone, forever. Forkers must stay open.

## The loop that makes it different

`Find -> Prove -> Fix -> Verify`, all on your machine, for free.

1. **Find** via static analyzers and model triage.
2. **Prove** by generating and (optionally) running a PoC that shows the actual crash.
3. **Fix** via the chat agent that edits the file with a real remediation.
4. **Verify** by re-scanning the changed file to confirm the bug is gone.

## The math (why you can trust it)

kwaro's differentiator is that confidence and termination are **derived from the
find/prove/fix/verify loop**, not asserted by the model. Four primitives make this
explicit and honest. All are pure stdlib Python, zero runtime deps, offline-friendly.
Full detail and verified examples are in [`docs/math.md`](docs/math.md).

- **Bayesian confidence.** Each finding starts from a low base rate (candidate flags are
  mostly noise, `prior = 0.05`). Evidence collected during prove/verify updates the
  posterior with Bayes rule. A finding is only reported if its posterior clears the bar.
  The model's own "I'm 90% sure" number is ignored.
- **Loop-variant termination.** The run state has a measure `V = unproven + unfixed +
  unverified`. Each pass strictly decreases `V` until it reaches 0 (or hits a safety cap),
  so the loop provably terminates. The trace is visible in output.
- **Pipeline graph + trace validator.** Find/Prove/Fix/Verify is a directed graph. A
  completed run must be a legal walk, so prove can never be silently skipped and every
  finding carries full lineage.
- **SPRT stop rule.** Wald's Sequential Probability Ratio Test sets error-rate budgets
  (`alpha` = false-positive rate, `beta` = missed rate) and stops as soon as the
  accumulated log-likelihood ratio crosses a bound. This controls both error rates by
  design instead of relying on an arbitrary threshold.

Example from [`docs/math.md`](docs/math.md): a real SQLi climbs from `posterior 0.05` to
`0.89` as static and PoC evidence arrives; a false alarm the model also rated 0.90
collapses to `0.02` because the verify stage found no real exposure. The math decides,
not the model.

## Features

| Feature | Status | Notes |
| --- | --- | --- |
| Static analyzers (secrets, SQLi, XSS, path traversal, weak crypto) | shipped | pure-Python, zero-dep, CWE-mapped |
| Domain profiles (generic, fintech, blockchain, ai_app) | shipped | select which analyzers run |
| Math spine (Bayes, variant, graph, SPRT) | shipped | drives confidence, ranking, termination |
| Pipeline ranking (L3 severity bands + composite confidence) | shipped | static > model, PoC-verified > unverified |
| De-duplication by root cause (L4) | shipped | merges by root cause, not tool output |
| SARIF 2.1.0 + JSON export | shipped | carries the math fields under properties |
| Diff-aware rescan (L9) | shipped | analyze changed files only |
| Browser UI via `serve` extra | shipped | hand-written bundle, no React build |
| CI/CD guard (`--diff` + SARIF) | planned | GitHub code scanning output |
| Tree-sitter AST detection | optional | per-language upgrade, off by default |

## Install

Pick whichever is easiest on your OS. The CLI has **zero third-party dependencies**
and one pure-Python wheel covers Windows, macOS, and Linux.

```bash
# PyPI (all OS)
pip install kwaro          # or: uv tool install kwaro

# macOS / Linux
brew install kwaro         # after: brew tap vip-ultr/kwaro

# Windows
scoop install kwaro        # after: scoop bucket add kwaro https://github.com/vip-ultr/scoop-kwaro

kwaro init                 # detect Ollama, write config (free/offline default)
```

The browser UI is an optional extra:

```bash
pip install "kwaro[serve]" # adds fastapi, uvicorn, websockets
```

For development from source:

```bash
git clone https://github.com/vip-ultr/kwaro
cd kwaro
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,serve]"
pytest                      # runs the suite + the in-repo fixture repo
```

## Quickstart

```bash
kwaro init                 # detect Ollama, recommend a local model
kwaro scan ./my-repo       # static-first scan, free, offline
kwaro chat ./my-repo       # conversationally find, prove, fix, verify
kwaro serve                # open the browser UI at http://127.0.0.1:8080
```

### CLI reference

```bash
kwaro init                                  # first run: detect Ollama, write config
kwaro scan ./my-repo                        # static scan + math spine, ranked report
kwaro scan ./my-repo --profile fintech      # domain-tuned analyzers
kwaro scan ./my-repo --rescan               # diff-aware: only changed files (L9)
kwaro scan ./my-repo --format sarif         # SARIF 2.1.0 export (math in properties)
kwaro scan ./my-repo --format json          # JSON export (L7 fields + math)
kwaro scan ./my-repo --pocs                  # generate PoC stubs per finding (offline)
kwaro chat ./my-repo                        # interactive loop: model uses tools, then reports
kwaro serve [--port 8080]                   # browser UI (needs the serve extra)
```

`kwaro chat` needs a model. With no model configured it falls back to the static
analyzer; point it at local Ollama (no key) or a hosted bring-your-own-key provider.

## Example scan output

```
kwaro: scanning ./my-repo (profile: generic, 5 analyzers, math spine on)

5 unique findings (from 5 raw), 0 kept after prove/verify

loop variant trace: 5 -> 5
pipeline graph valid: True (ok)
de-duplicated: 5 raw -> 5 unique

severity | rule                 | file:line        | confidence
---------|----------------------|------------------|-----------
HIGH     | secrets.hardcoded     | app.py:1          | static
HIGH     | injection.sql-concat  | app.py:3          | static
MEDIUM   | xss.innerhtml        | static/bundle.js:5| static
MEDIUM   | traversal.open-userpath| server.go:9      | static
MEDIUM   | auth.weak-hash       | app.py:7          | static
```

Each finding carries its posterior, SPRT verdict, composite confidence, and PoC state,
exposed in the terminal report, the browser UI, and the SARIF/JSON export.

## Results (eval, L13)

The seeded fixture [`tests/fixtures/vuln-repo/`](tests/fixtures/vuln-repo/) contains one
instance of each detector. [`tests/test_eval.py`](tests/test_eval.py) asserts recall
(every seeded rule fires) and flags unexpected rule ids as possible false positives.

Current numbers on the fixture: **100% recall** on the 5 seeded rule families (secrets,
SQLi, XSS, traversal, weak crypto), **0 unexpected findings**. The math spine keeps
0 of 5 static candidates in the "kept" set because offline static evidence alone does
not clear the posterior bar or the SPRT `REAL` verdict, which is the honest behavior
until a PoC verifies. As the loop gains prove/verify evidence (see
[`docs/math.md`](docs/math.md)), that SQLi posterior rises to 0.89 and the finding is
kept; a false alarm collapses and is dropped. Precision/recall tracking per scan is the
product's headline quality metric, not raw "findings found."

## Privacy and security posture

kwaro is a local scanner. The [`SECURITY.md`](SECURITY.md) policy is explicit:

- With the default local provider (Ollama), nothing leaves your machine. No code,
  snippets, or findings are uploaded anywhere.
- The only network traffic is what you opt into: a non-local provider, or an explicit
  version check (off by default).
- Proof-of-concept execution is off by default. When enabled, it runs in a separate
  process with a temp directory, no network, and resource/time limits. It is a soft
  boundary, not a hard sandbox. Run untrusted PoCs in a container or VM you can discard.
- kwaro complements, not replaces, expert review and mature SAST tools. Model output can
  be wrong; findings tagged `model-only` or `unverified` are lower-confidence by design.

## Architecture at a glance

```
kwaro/
  core/         models, storage (SQLite), workspace, verify (Bayes + SPRT),
                graph (trace validator), loop (variant termination),
                rank (L3 bands + confidence), pipeline (FIND/PROVE/FIX/VERIFY),
                profiles, export (SARIF + JSON)
  analyzers/    base + registry, secrets, injection, xss, traversal, auth, prover
  providers/    base, ollama (offline default), openai-compat (BYOK)
  chat/         agent (tool-calling loop, deterministic validation)
  web/          static bundle (index.html, style.css, app.js), no React build
  serve.py      FastAPI app (lazy import; CLI stays zero-dep)
```

The CLI stays zero-dependency. FastAPI/uvicorn/websockets load only under `kwaro serve`.
Detailed design and locked decisions: [`docs/architecture.md`](docs/architecture.md),
[`docs/locked-decisions.md`](docs/locked-decisions.md).

## Development status

Phases 0-6 are shipped and verified (pytest green, 35/35). The CI matrix runs on
ubuntu/macos/windows across Python 3.10-3.12. The only remaining pre-1.0 items are a
launch demo and the optional PyPI publish step (a maintainer action). See
[`docs/roadmap.md`](docs/roadmap.md) and [`BUILD.md`](BUILD.md) for the phase history.

## Documentation

All planning, research, and locked decisions are in [`docs/`](docs/):

- [`docs/math.md`](docs/math.md) - the math spine (Bayes, variant, graph, SPRT) with verified examples
- [`docs/locked-decisions.md`](docs/locked-decisions.md) - the locked engineering decisions (L1-L14)
- [`docs/game-changers.md`](docs/game-changers.md) - the differentiators that define the product
- [`docs/architecture.md`](docs/architecture.md) - module layout and data flow
- [`docs/profiles.md`](docs/profiles.md) - how to write a domain profile
- [`docs/release.md`](docs/release.md) - versioning and release process
- [`BUILD.md`](BUILD.md) - build handoff and resume point

Community guidelines: [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md),
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Contributing

Contributions of all kinds are welcome: code, domain profiles, docs, bug reports, and
ideas. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md). The easiest high-value
contribution is a domain profile (see [`docs/profiles.md`](docs/profiles.md)). All
commits are Developer Certificate of Origin (DCO) signed-off (`git commit -s`).

## License

AGPL-3.0. See [LICENSE](LICENSE). Free for everyone, forever; forkers must stay open.
