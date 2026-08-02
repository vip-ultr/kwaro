# kwaro - LOCKED DECISIONS (from research)

These are the final, locked design choices distilled from docs/research.md and
docs/decisions-unlocked.md. Build against these. Anything not here is still open.

## L1. Free-first, local-first, zero-dependency runtime
- Default provider: Ollama, local, offline, no key. Paid is opt-in via OpenAI-compatible API.
- Runtime has ZERO third-party deps for the CLI. `serve` extra adds fastapi/uvicorn/websockets only.
- Single language: Python 3.10+. Pure stdlib (pathlib, subprocess list-args). Cross-OS.

## L2. Static analysis = hybrid, regex is the always-available layer
- v1: regex/line-heuristic analyzers, zero extra deps, cover secrets, SQLi, XSS,
  path traversal, auth gaps, across Python/JS/TS/Go/Java/PHP/Solidity/Rust where patterns apply.
- Tree-sitter is an OPTIONAL per-language upgrade (off by default, install on demand) for
  AST/multi-line data-flow detection. Regex is the fallback layer, not the whole story.

## L3. Severity = CVSS-style bands + composite confidence
- Bands: Critical 9.0-10, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9, Info <0.1.
- Composite signal raises/lowers confidence (not band alone):
  static-confirmed > model-only; PoC VERIFIED > UNVERIFIED; tree-sitter data-flow > heuristic.
- We do NOT claim CVSS-precise vectors. Bands are qualitative.

## L4. De-duplication by ROOT CAUSE
- Dedup key = ruleId + normalized file + normalized line + normalized snippet hash.
- Cross-scan stability via SARIF partialFingerprints. Findings merge by root cause, not tool output.

## L5. Tool-call robustness (deterministic, never trust raw model output)
- Tools = strict JSON schemas; validator checks name known + args parse + required present.
- Invalid -> re-inject correction as tool-result, retry up to N, then step falls back to static-only.
- Capability gating: models below a known-good tool-calling tier -> warn, offer chat/static mode.
- Streaming: accumulate full tool_call JSON before parsing.

## L6. PoC honesty + sandbox limits (explicit)
- Lifecycle: GENERATED -> COMPILED -> EXECUTED -> VERIFIED | UNVERIFIED.
- VERIFIED only if it runs AND triggers expected failure. UNVERIFIED never raises severity.
- Execution OFF by default. When on: temp dir, no network, resource limits, timeout, kill on breach.
- Print: "Not a hard security boundary; run untrusted PoCs in a container/VM."

## L7. Data model (exact)
- Finding: id, scan_id, title, severity, cwe, rule_id, source(static|model|static+model),
  confidence(low|med|high), file, line_start, line_end, column, snippet, description,
  suggested_fix, poc_path, poc_state(none|generated|verified|unverified), fingerprint, created_at.
- Scan: id, target, target_type(local|git), commit, provider, model, profile, status,
  started_at, finished_at, finding_count.
- StepResult: id, scan_id, step_index, name, raw_output, tool_calls(json), findings(json), duration_ms.

## L8. Storage = SQLite, one file, zero-config
- `~/.kwaro/kwaro.db`. No server, no migrations framework. Schema additive, versioned in code.

## L9. Diff-aware rescan
- git target: store last scanned commit per (target, profile); rescan analyzes `git diff --name-only`.
- local path: store file hash (mtime+size+sha) per profile; analyze changed files only.
- Unchanged findings persist; vanished-file findings marked resolved. Baseline in SQLite.

## L10. Chat state (privacy by default)
- In-memory per session; NO cross-session memory by default. Context = active workspace + findings.
- Model calls tools only within the active workspace. Loop ends when model returns no tool calls.

## L11. UI: single static bundle, no React build in v1
- Hand-written CSS (locked palette), vanilla JS + tiny helper (or htmx/Alpine via CDN).
- FastAPI serves bundle + WebSocket for live activity/chat. `serve` extra only.

## L12. Packaging + first-run
- pip/uv primary; git clone runs via module. Later: Homebrew tap.
- First run with no config -> `kwaro init`: detect Ollama, recommend 14B agent model, explain
  free/offline, write `~/.kwaro/config.toml`. Static-only works with no model.

## L13. Evaluation = in-repo fixture + eval
- `tests/fixtures/vuln-repo/` seeded per rule + per domain. Eval asserts recall + reports FP.
- README shows real numbers. Doubles as launch demo.

## L14. Brand / naming
- Single logo (aperture chevron, ink + lime). No competitor names anywhere in product.
- Agents are anonymous steps, not named personas (option A).
