# Contributing to kwaro

kwaro is a free, open-source security scanner for every developer. We welcome
contributions of all kinds: code, domain profiles, docs, bug reports, and ideas.

## Ways to contribute

- **Report bugs** via GitHub Issues. Include the target, command run, provider/model,
  and the actual vs expected behavior. For security-sensitive findings, see SECURITY.md.
- **Propose features** via Issues or Discussions before large PRs.
- **Add a domain profile** (see `docs/profiles.md`). Profiles are the easiest high-value
  contribution and feed the community growth loop.
- **Write code.** Follow the setup below.

## Development setup

```bash
git clone https://github.com/vip-ultr/kwaro
cd kwaro
python -m venv .venv && source .venv/bin/activate   # or: uv venv && uv shell
pip install -e ".[dev,serve]"                         # or: uv pip install -e ".[dev,serve]"
pytest                                             # runs the suite + fixture repo
```

Runtime has **zero third-party dependencies** for the CLI. `dev` adds pytest;
`serve` adds the optional browser UI deps (fastapi, uvicorn, websockets).

## Coding standards

- Python 3.10+. Stdlib only in `kwaro/` runtime code (no new runtime deps without
  discussion). `serve/` and `dev` may use their declared extras.
- Format: `ruff format` (or black-equivalent). Lint: `ruff check`. Type hints required
  on public functions.
- Every public behavior gets a test. Static analyzers need positive AND negative
  fixtures in `tests/fixtures/`.
- Keep findings honest: never raise severity on an unverified PoC (see docs/locked-decisions.md L6).

## Commits and sign-off

We use the Developer Certificate of Origin (DCO). Sign your commits:

```bash
git commit -s -m "analyzers: add GraphQL injection rule"
```

The `-s` adds `Signed-off-by: Your Name <you@example.com>`. Set your git identity:

```bash
git config user.name  "Your Name"
git config user.email "you@example.com"
```

PRs without sign-off are not merged.

## Domain profiles

A profile is a plain file pairing static rules + a triage prompt for a domain
(fintech, blockchain, AI apps). Format and discovery are specified in
`docs/profiles.md`. Profiles are reviewed like code; a maintainer merges after a
sanity check on false-positive rates using the fixture repo.

## Code of Conduct

Be respectful. Harassment, insults, or dismissive behavior are not tolerated.
Reports go to the maintainers via a private GitHub message.

## Review process

1. Open a PR against `master` with a clear description and linked Issue.
2. CI must pass (lint + tests on Linux/macOS/Windows).
3. A maintainer reviews for correctness, false-positive risk, and adherence to the
   locked decisions.
4. Once approved and signed-off, it is merged.

Thank you for making security tooling free and local for everyone.
