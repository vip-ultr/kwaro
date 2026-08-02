# kwaro - Research on UNLOCKED areas

Research into parts of the plan that were not yet locked. Each section ends with a
**Decision** that should be promoted into architecture.md once accepted. Last
review: 2026-08-02.

## U1. Static analysis implementation approach

**Research:** Regex/line matching misses multi-line source-sink flows (known
limitation in regex-based scanners). AST/tree-sitter detection catches those and is
what serious tools (Semgrep) use. Tree-sitter's runtime is C11, dependency-free to
embed, but each language needs its own grammar binding (a native package). Pure
regex is the always-available fallback; tree-sitter is the accuracy upgrade.

**Decision (proposed):**
- v1 ships a regex/line-heuristic layer that works with ZERO extra dependencies and
  covers secrets, SQLi, XSS, path traversal, auth gaps, for common languages
  (Python, JS/TS, Go, Java, PHP, Solidity, Rust) via language-agnostic patterns
  where possible.
- Tree-sitter is an OPTIONAL upgrade (off by default, installed on demand) for
  AST-aware, multi-line data-flow detection, per language as grammars are added.
- Frame regex as the fallback layer, not the whole story, in docs. Roadmap notes
  tree-sitter as a Phase 4+ enhancement.
- Keep analyzers as pure Python; no heavy SAST dependency required to run.

## U2. Severity ranking + de-duplication

**Research:** CVSS is the dominant standard but FIRST explicitly warns base scores
should not be used alone for prioritization; only ~2.3% of CVSS>=7 CVEs were
observed exploited in a month. Best practice: composite risk score, dedup by ROOT
CAUSE (not by tool output), and contextual signals (exploitability, confidence,
static vs model-only).

**Decision (proposed):**
- Severity bands map to CVSS-style ranges: Critical 9.0-10, High 7.0-8.9,
  Medium 4.0-6.9, Low 0.1-3.9, Info <0.1. (Qualitative, not a full CVSS vector calc.)
- Composite signal on top of the band:
  - static-confirmed (higher) vs model-only (lower)
  - PoC VERIFIED (raise confidence, not necessarily band) vs UNVERIFIED
  - data-flow confidence from tree-sitter when available
- De-duplication key = root cause hash: ruleId + normalized file path + normalized
  line + normalized snippet. Cross-scan dedup uses SARIF partialFingerprints. This
  makes rescans stable and findings merge correctly.

## U3. PoC execution sandbox

**Research:** Pure-Python sandboxing is unsafe (trivial escapes documented). Real
isolation needs OS-level controls (seccomp + setrlimit on Linux; native lib
required) or container/VM. subprocess with resource limits + no network + temp dir
is a reasonable soft boundary but NOT a hard security boundary.

**Decision (proposed):**
- PoC EXECUTION is OFF by default (G2/G5).
- When enabled via explicit `--execute-poc`, run in a separate process: temp dir
  only, no network (best-effort: block sockets / use firewall-less isolated netns
  where available), CPU/time/memory limits via setrlimit/timeout, killed on breach.
- Print a clear warning: "Not a hard security boundary; run untrusted PoCs in a
  container or VM." Recommend Docker/VM for untrusted targets.
- VERIFIED requires the PoC to actually trigger the expected failure; otherwise
  UNVERIFIED. Never imply execution = safety.

## U4. Data model (exact fields)

**Decision (proposed) - promote to architecture.md:**
- `Finding`: id, scan_id, title, severity (enum), cwe (e.g. CWE-89), rule_id,
  source ("static"|"model"|"static+model"), confidence ("low"|"medium"|"high"),
  file, line_start, line_end, column, snippet, description, suggested_fix,
  poc_path (nullable), poc_state ("none"|"generated"|"verified"|"unverified"),
  fingerprint (dedup key), created_at.
- `Scan`: id, target, target_type ("local"|"git"), commit (nullable), provider,
  model, profile (e.g. "fintech"), status, started_at, finished_at, finding_count.
- `StepResult`: id, scan_id, step_index, name, raw_output (text), tool_calls (json),
  findings_extracted (json), duration_ms.

## U5. Diff-aware rescan

**Decision (proposed):**
- For git targets, store the last scanned commit per (target, profile). On rescan,
  compute `git diff --name-only <baseline> <HEAD>`; analyze only changed files.
- For local paths, store file hashes (mtime+size+sha) per profile; analyze only
  changed files.
- Findings from unchanged files persist; new/changed files produce new findings;
  findings whose file vanished are marked resolved. Baseline stored in SQLite.

## U6. Chat loop state

**Decision (proposed):**
- `kwaro chat` maintains an in-memory conversation (messages + tool results) for the
  session; no cross-session memory by default (privacy). Context = current scan's
  workspace + findings. The model may call tools (read file, run analyzer, request
  PoC) within the active workspace only.
- Multi-turn: each user message appends; tool results feed back; loop ends when the
  model returns no tool calls. Clear "exit" command. Conversation can be saved to a
  scan record optionally.

## U7. Browser UI framework

**Decision (proposed):**
- v1: single static bundle, hand-written CSS (locked palette), vanilla JS + a tiny
  reactivity helper (or htmx/Alpine via CDN). Served by FastAPI. WebSocket streams
  agent activity + chat. NO React/Node build step (keeps zero-dep promise for CLI;
  `serve` extra only adds fastapi/uvicorn/websockets).
- Revisit React only if the UI outgrows vanilla; not in v1.

## U8. Packaging / first-run UX

**Decision (proposed):**
- Primary: `pip install kwaro` / `uv tool install kwaro`. Also `git clone` + run
  module (no install). Later: Homebrew tap, optional install.sh (secondary).
- First run of any command with no config triggers `kwaro init` flow: detect Ollama,
  recommend a 14B agent model, explain free/offline, write `~/.kwaro/config.toml`.
- Static-only mode works with no model; agent mode requires a capable provider.

## U9. Evaluation / fixture repo

**Decision (proposed):**
- `tests/fixtures/vuln-repo/` seeded with one vulnerability per rule + per domain
  profile. Eval script asserts recall (found/seed) and reports false positives on
  clean code. README shows real numbers. Doubles as launch demo.
