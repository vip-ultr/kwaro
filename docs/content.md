# kwaro - Content & Copy Spec

The words kwaro uses. Voice, UI strings, finding copy, chat messages, errors, and
launch text. Written to match the brand: precise, professional, honest about
confidence, no hype. Follows the project writing rules: no em dashes, quantities as
digits, sharp and direct.

## Voice principles

1. Precise over polite. Say what happened, not "we regret to inform you."
2. Honest about confidence. Separate what we KNOW (static hit, verified PoC) from
   what we GUESS (model-only). This is the trust engine (GC6).
3. No hype words. No "revolutionary", "seamless", "blazing". Describe behavior.
4. Short sentences. One idea per line in UI. Full sentences in docs.
5. Active voice. "kwaro found 3 findings" not "3 findings were found by kwaro."
6. Numbers as digits. "14B model", "9.0", "3 findings", not "fourteen" or "nine point oh".

## Terminal copy

### Banner (kwaro with no args / version)
```
kwaro 0.1.0  -  free, local security scanner
scan any codebase. prove findings. fix and verify. offline by default.
```

### First run (inline init, from fail-states.md)
```
kwaro: no config found. Setting up (free, local, offline by default)...
  [1/3] Looking for Ollama... found at http://localhost:11434
  [2/3] Recommended model: qwen3:14b (~9GB RAM) for agent + PoC mode
        pull it:  ollama pull qwen3:14b
  [3/3] Wrote ~/.kwaro/config.toml
Scanning in STATIC-ONLY mode (no model). Add a provider with: kwaro init
```

### Scan start
```
kwaro: scanning ./my-repo  (profile: generic, mode: static+model)
kwaro: analyzed 42 files, 3 findings
```

### Findings summary (end of scan)
```
3 findings   2 high   1 medium

  HIGH   ./src/db.py:88      SQL injection (CWE-89)        proven
  HIGH   ./src/auth.py:14    Missing auth check (CWE-287)  static
  MEDIUM ./src/util.py:33    Hardcoded secret (CWE-798)    static

Run `kwaro prove <id>` to reproduce, or `kwaro chat ./my-repo` to fix.
```

### Prove command
```
kwaro: generating PoC for ./src/db.py:88 ...
kwaro: running PoC in sandbox (no network, temp dir) ...
PoC RESULT: VERIFIED
  reproduced: unhandled exception on crafted input at db.py:91
  proof: /home/you/.kwaro/pocs/2026-08-02-abc123.py
```

### Prove unverified
```
kwaro: PoC ran but did not trigger the expected failure.
       marked UNVERIFIED. Review the snippet and model note manually.
```

## Browser UI copy

### App shell
- Title bar: `kwaro`  (logo + wordmark, lime accent on the mark)
- Nav: `Scans`  `Chat`  `Profiles`  `Settings`
- Empty state (Scans): "No scans yet. Drop a repo path or URL to start. Your code
  stays on this machine."
- Empty state (Chat): "Ask kwaro to find, prove, fix, or verify. The agent works
  only inside the repo you opened."

### Finding card
```
[severity pill]  title                        [proven | static | model]
file:line
why: one plain sentence on impact for THIS app.
rule: CWE-89 · source: static+model · confidence: high
[View snippet] [Prove] [Fix] [Ignore]
```
- "why" is generated from the model reading surrounding code (GC8), not a CWE paste.
- Proven badge shows only when poc_state = verified.

### Live activity rail (right or bottom)
```
cloning repo ...
analyzing 42 files (static) ...
triage: 3 candidates (model) ...
proving ./src/db.py:88 ...
verified.
```
Each line is a stage label, not a named agent persona (option A).

### Settings
- Provider: `Ollama (local, offline)` default. "Your code is not sent anywhere in
  this mode."
- Execute PoC: toggle, OFF by default. Helper: "Runs generated code in a sandbox.
  Not a hard security boundary. Use a container for untrusted code."

## Chat messages (agent -> user)

System intro (first chat message):
```
I can find, prove, fix, and verify vulnerabilities in ./my-repo.
I read only this workspace. Nothing leaves your machine in local mode.
Try: "scan for auth issues", "prove the SQLi at db.py:88", "fix it".
```

Confirming a fix:
```
Applied fix to ./src/db.py:88 (parameterized the query).
Re-scanning that file ...
VERIFIED: the SQLi finding is closed. No new findings introduced.
```

Honesty when unsure:
```
This looks like a real issue but I could not build a confident PoC locally.
Marked model-only, confidence medium. Review the snippet before acting.
```

## Error strings (mirror fail-states.md)

- Ollama down: `kwaro: cannot reach Ollama at http://localhost:11434. Start it: ollama serve`
- Model missing: `kwaro: model 'qwen3:14b' not found. Pull it: ollama pull qwen3:14b`
- Weak tool-calling: `kwaro: model '<x>' has weak tool-calling. Using STATIC-ONLY for this step. Use a 14B+ model for agent mode.`
- Cyber-safety block: `kwaro: provider blocked this request (cyber-safety policy). Local models do not. Switch provider or use Ollama.`
- Target missing: `kwaro: target '<x>' not found.`
- Scan interrupted: `kwaro: scan stopped. Partial findings saved.`

All errors name the fix as a command. None imply success.

## README sections (prose, beyond the stub)

### Tagline
`A free, open-source security scanner for every developer, on every OS.`

### One-line pitch
`kwaro finds vulnerabilities in your code with a local AI agent, then proves them
with a runnable exploit and helps you fix and verify, all on your machine, for free.`

### "Why local"
`Cloud scanners upload your code. For banking, fintech, and blockchain teams that is
a compliance blocker. kwaro runs fully offline on a local model. Your source never
leaves the machine, and no provider can refuse a security prompt for cyber-safety
reasons.`

### "The loop"
`Find via static analysis and model triage. Prove by generating and running a PoC
that shows the crash. Fix via the chat agent. Verify by re-scanning. One session,
one machine, zero cost.`

## Launch post (lead with the demo, GC1)

Title: `kwaro: a free, local security scanner that proves its findings`

Body (short):
```
Most scanners tell you "maybe a bug." kwaro proves it.

It scans your repo with a local model (Ollama, offline, free), finds
vulnerabilities, then generates and RUNS a proof-of-concept that shows the actual
crash. Then it offers to fix the file and re-scans to confirm it is closed.

No code leaves your machine. No paid API required. Works on any codebase, with
community domain profiles for fintech, blockchain, and AI apps.

Try it: pip install kwaro && kwaro init && kwaro scan ./your-repo
```

Keep it under 200 words. Show the GIF of Find->Prove->Fix->Verify.

## Microcopy rules

- Buttons: verb-led. `Scan`, `Prove`, `Fix`, `Ignore`, `Re-scan`. Not `Submit Scan`.
- Confirmations: state the outcome. `VERIFIED` / `CLOSED` / `SAVED`, not `Done`.
- Never "Oops". Errors are statements, not apologies.
- Time: digits. `scan took 12s`, not `twelve seconds`.
