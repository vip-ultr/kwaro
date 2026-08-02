# kwaro - Research & Feasibility (living doc)

Deep research on the locked plan. Verified against primary sources where possible.
Updated as we learn more. Last review: 2026-08-02.

## 1. Local model tool calling (CORE assumption) — VERIFIED, with caveats

Our agent loop depends on the model calling tools (read file, run analyzer, request
PoC). Ollama's official API supports tool/function calling via `POST /api/chat`
with a `tools` array (OpenAI-style function schema). Confirmed working with
`qwen3` and `llama3.2` in Ollama docs.

**Caveat (verified, important):** tool-calling reliability varies sharply by model.
Community/benchmark consensus (2025-2026): stable for Qwen3 (8B/14B/32B) and
Llama 3.1/3.3; flaky on small 7B-class models (malformed/omitted tool calls).

## 2. SARIF export — VERIFIED, low risk

SARIF 2.1.0 is an OASIS standard with a published JSON schema
(`sarif-schema-2.1.0.json`). Structure: `version`, `$schema`, `runs[]`, each run
has `tool.driver` (name, rules[]) and `results[]` (ruleId, level, message,
locations[].physicalLocation.region, partialFingerprints). `partialFingerprints`
is our de-duplication key across rescans.

## 3. Local LLM PoC / test generation (THE differentiator + THE risk) — PARTIAL

Benchmarks (EXPLOITBENCH for V8 exploitation, SEC-bench Pro, ACL 2025 vuln-agent
papers) show LLMs struggle with long-horizon exploit correctness. A 2025 study
found ~40% of GitHub Copilot completions were vulnerable. Generating a PoC that
actually compiles and reproduces requires build/runtime understanding local 7B-14B
models do imperfectly.

## 4. Cross-OS, zero-dep, single-language — VERIFIED, low risk

Pure Python stdlib, `pathlib`, `subprocess` with list args, no compiled extensions.
Runs on Windows/macOS/Linux/WSL.

## 5. Free-first / offline — VERIFIED, strong position

Ollama runs fully offline, no key, no cyber-safety blocks. Paid providers may
refuse security-research prompts; local models do not.

## 6. Detection breadth vs incumbents — HONEST GAP

We will not match Semgrep/CodeQL/SAST on day-one rule coverage. Our edge is free +
local + agentic triage + PoC proof + any-domain via prompts. Claim "free, local,
proves findings, works on any code," not "finds more than X."

---

# Resolved solutions to the gaps (professional design)

## G1. Tool-call robustness — deterministic protocol, never trust raw output

- Tools defined as strict JSON schemas in `core/providers/tools.py`. After each
  model turn, a validator checks: function name is known, arguments parse to the
  schema, required fields present.
- On invalid call: re-inject a system correction as a tool-result message
  ("last tool call invalid: <reason>; retry with valid JSON") and retry up to N.
  After N, that step falls back to static-only mode (no model tool use).
- Capability gating: at init, check the configured model against a tier list. If
  below a known-good tool-calling tier, warn and offer chat/static mode instead of
  agent mode. Never assume a 7B model emits valid tool calls.
- Streaming: accumulate the full tool_call JSON before parsing; never parse partial
  streamed fragments.

## G2. PoC honesty — explicit verification states, never implied proof

- PoC lifecycle: GENERATED -> (opt) COMPILED -> (opt) EXECUTED ->
  VERIFIED or UNVERIFIED.
- Verification runs in a sandbox: temp dir, no network, CPU/time/memory limits,
  restricted filesystem. A PoC is VERIFIED only if it runs AND triggers the
  expected failure (non-zero exit / assertion / crash signature requested).
  Otherwise UNVERIFIED, labelled clearly.
- An UNVERIFIED PoC never auto-raises a finding's severity/confidence. The PoC is
  supporting evidence, not authority.
- Finding record stores the PoC file path + its run result so the user sees exactly
  what was (or wasn't) proven.

## G3. Default model guidance — curated catalog with tiers

- Ship `core/providers/model_catalog.py`: tiers `agent` (tool-calling capable),
  `chat` (explain-only), `avoid` (known-bad tool calling).
- `kwaro init` recommends a 14B-class agent model and states RAM needs.
- User override allowed. If a chat-tier model is chosen, agent mode is disabled with
  a clear message.

## G4. Static-first pipeline — model triages, does not invent

- Order: static analyzers run first -> candidate findings with rule IDs.
- The model is given ONLY those candidates (file + line + rule + snippet) and asked
  to confirm/refute with reasoning. Findings without static backing are marked
  "model-only, lower confidence."
- This keeps false positives down: the model explains real signals, not imagined ones.

## G5. Trust/safety — explicit, unavoidable communication

- README and first-run output state: scans run locally; code is not uploaded; PoC
  execution is opt-in, sandboxed, disabled by default.
- Ship `SECURITY.md` (threat model) documenting capabilities, limits, sandbox bounds.
- `kwaro scan --execute-poc` requires an explicit flag + printed warning; never silent.

## G6. Benchmark ourselves — fixture repo + eval in the repo

- Ship `tests/fixtures/vuln-repo/` seeded with known vulnerabilities (one per rule:
  secrets, SQLi, XSS, traversal, auth; plus per-domain profiles).
- An eval script runs kwaro and asserts each seeded bug is found (recall) and reports
  false-positive count on clean code.
- README shows real numbers ("found 11/12 seeded vulns on model X, 0 FP on clean
  code") instead of vibes. This is also the launch/demo material.

---

## Verdict

Plan is technically sound. Differentiators (free/local, SARIF, PoC proof, any-domain)
are real and verifiable. The two real risks, tool-call reliability (G1) and PoC
correctness (G2), are resolved by deterministic validation and explicit verification
states. We build G1/G2/G4 into the engine from day one; G3/G5/G6 are setup, docs,
and eval that make the product trustworthy and demonstrable.
