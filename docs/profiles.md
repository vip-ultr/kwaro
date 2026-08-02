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

## Why this is a moat

Anyone can write a profile for their stack and PR it. Over time kwaro accumulates
expert scanners for domains no single vendor funds, contributed by the people who
know those domains. That is the open-source growth engine (GC5).
