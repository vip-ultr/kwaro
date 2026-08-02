# Fail States & First-Run UX

The difference between a starred tool and a "doesn't work" issue is what the user
sees when something goes wrong. This specifies kwaro's failure behavior and the
first-run flow (locked-decision L12, game-changer GC6 honesty).

## Design principles

- Fail loud, fail clearly, never silently. Every error tells the user what happened
  and the exact next command to fix it.
- Never imply success. A partial scan is reported as partial.
- Privacy-respecting messages: we never print code contents in errors.

## First run (no config)

`kwaro scan <target>` with no `~/.kwaro/config.toml` triggers `kwaro init` inline:

```
kwaro: no config found. Setting up (free, local, offline by default)...
  [1/3] Looking for Ollama... found at http://localhost:11434 (or: not running)
  [2/3] Recommended model: qwen3:14b  (~9GB VRAM/RAM) for agent + PoC mode
        -> pull with: ollama pull qwen3:14b   (or pick a smaller chat model)
  [3/3] Wrote ~/.kwaro/config.toml
Scanning in STATIC-ONLY mode (no model). Add a provider anytime with `kwaro init`.
```

Static-only mode works with no model. Agent/PoC mode requires a capable provider.

## Provider / model failures

| State | Message |
|-------|---------|
| Ollama not running | `kwaro: cannot reach Ollama at http://localhost:11434. Start it: \`ollama serve\`, or set a cloud provider in config.` |
| Model not pulled | `kwaro: model 'qwen3:14b' not found locally. Pull it: \`ollama pull qwen3:14b\`.` |
| Tool calls unreliable (small model) | Warn once: `kwaro: model '<x>' has weak tool-calling; using STATIC-ONLY for this step. Use a 14B+ model for agent mode.` |
| Paid provider refuses (cyber-safety) | `kwaro: provider blocked this request (cyber-safety policy). Local models do not. Switch provider or use Ollama.` |

## Scan failures

| State | Behavior |
|-------|----------|
| Target not found | Exit non-zero with `kwaro: target '<x>' not found.` |
| Git clone fails | Report the git error; do not create a partial workspace. |
| Analyzer crash on a file | Skip that file, log `warn: skipped <file>: <err>`, continue. Summary shows skipped count. |
| Model call times out | Retry once; on second timeout, mark step STATIC-ONLY, continue. |
| Scan interrupted (Ctrl-C) | Graceful shutdown; partial findings saved; exit code 130. |

## PoC execution failures (opt-in)

| State | Behavior |
|-------|----------|
| `--execute-poc` set but sandbox unsupported | Print warning, run with soft limits, remind: use a container/VM. |
| PoC does not reproduce | Finding stays `poc_state=unverified`; message: `PoC ran but did not trigger the expected failure (unverified).` |
| PoC crashes sandbox / timeout | Kill process; `poc_state=unverified`; never mark VERIFIED on a crash. |

## Output on success

- Terminal: ranked findings, severity pill, file:line, one-line why, `proven` badge
  when VERIFIED. Ends with counts + `kwaro prove <id>` hint.
- JSON/SARIF: full structured output for CI.
- Exit code 0 if scan completed (even with findings); 1+ only on hard failure.

## Honesty in UX

Every finding shows its evidence chain (GC6): `static` / `model` / `verified`.
Users trust kwaro because it says what it KNOWS vs GUESSES. This is a feature, not
a disclaimer.
