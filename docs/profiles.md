# Domain Profiles

A profile tailors kwaro to a domain (fintech, blockchain, AI apps) by pairing
static rules with a triage prompt. Profiles are plain, reviewable files, the core
of kwaro's "any codebase, expert results" promise (game-changer GC5). This is the
format and discovery spec (locked-decision L7-adjacent).

## Location and discovery

- Built-in profiles live in `kwaro/core/profiles/<name>.toml`.
- User profiles live in `~/.kwaro/profiles/<name>.toml` (or `--profile-path`).
- Select with `kwaro scan --profile fintech`. Default: `generic`.

## File format (TOML)

```toml
name = "fintech"
description = "PCI/auth-focused scanning for payment and banking code"
cwe_focus = ["CWE-287", "CWE-532", "CWE-327"]   # surfaced as priorities

[static]
# references built-in analyzer rule ids to enable/weight
enable = ["secrets", "injection", "auth", "traversal"]
# domain-specific regex patterns (kept minimal; AST upgrade later)
rules = [
  { id = "FIN-001", cwe = "CWE-532", severity = "medium",
    pattern = "panic\\(.*(card|cvv|pan)\\)", message = "Logs sensitive payment data" },
]

[triage]
# prompt appended to the model when confirming candidates
system = """
You are a payments-security reviewer. Confirm only findings that realistically
affect auth, PCI data, or money movement. Reject theoretical issues without a
concrete exploit path in THIS codebase. For each confirmed finding, explain the
impact in one sentence for a non-security engineer.
"""
```

## Rules

- `id`: unique within the profile (namespaced, e.g. `FIN-001`).
- `cwe`: maps to a CWE for SARIF/Grouping.
- `severity`: critical|high|medium|low|info (band per locked-decision L3).
- `pattern`: a line regex (Python `re`, MULTILINE). Multi-line flows use the
  optional tree-sitter layer (future), matched by `ast_query` instead.
- `message`: shown to the user.

## Triage prompt

The `[triage]` system prompt is added to the model context when it confirms the
static candidates. It encodes domain judgment (what counts, what to ignore) so
results are expert-level, not generic.

## Review and merge (community loop)

- A new profile is a PR against `kwaro/core/profiles/`.
- Maintainers run the fixture repo eval (`pytest tests/`) and check false-positive
  rate before merge. A profile that floods false positives is sent back.
- Profiles are plain text, easy to audit, and credited to the author.

## Coverage model (locked stance)

We do NOT hand-add every domain in the world. The model is:

- **Seed a few, community extends the rest.** kwaro ships a small set of curated
  profiles we know well: `generic` (default), `fintech`, `blockchain` (Solidity),
  `ai-app`. That is ~3-4, not exhaustive.
- **Anyone can add a domain.** A profile is one plain TOML file (rules + triage
  prompt). A healthcare, IoT, WordPress, Rails, or Kubernetes-config expert writes
  one and opens a PR. The burden of domain coverage is distributed, not on us.
- **Quality gate.** Maintainers run the fixture-repo eval and check false-positive
  rate before merge. Weak profiles are sent back. Confidence is shown per finding.
- **"Expert" means security patterns, not business logic.** A fintech profile traps
  PCI/auth patterns; it does not understand the app's business semantics. A profile
  is only as good as its author, which is why the eval gate exists.

This is the open-source growth engine (GC5): we build the engine + seed profiles +
quality gate; the community extends coverage to every domain that matters to them.
