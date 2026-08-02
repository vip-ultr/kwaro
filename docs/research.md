# kwaro - Research & Feasibility (living doc)

Deep research on the locked plan. Verified against primary sources where possible.
Updated as we learn more. Last review: 2026-08-02.

## 1. Local model tool calling (CORE assumption) — VERIFIED, with caveats

Our agent loop depends on the model calling tools (read file, run analyzer, request
PoC). Ollama's official API supports tool/function calling via `POST /api/chat`
with a `tools` array (OpenAI-style function schema). Confirmed working with
`qwen3` and `llama3.2` in Ollama docs.

**Caveat (verified, important):** tool-calling reliability varies sharply by model.
Community/benchmark consensus (2025-2026):
- Stable for tool calling: Qwen3 (8B/14B/32B), Llama 3.1/3.3.
- Flaky on small models (7B-class): tool_calls often malformed or omitted.

**Decision/impact:**
- Default recommended model should be Qwen3:14B or Llama3.1:8B+ (NOT a tiny 7B) for
  reliable tool use. Document this. Smaller models = chat only, degraded agent.
- The agent loop must be robust to malformed/omitted tool calls (retry, parse
  fallback, never assume the model emits valid JSON). This is a build requirement,
  not optional.
- For users without a capable local model, the agent still works in "static-only"
  mode (no model needed), so tool-calling is an enhancement, not a hard dependency.

## 2. SARIF export — VERIFIED, low risk

SARIF 2.1.0 is an OASIS standard with a published JSON schema
(`sarif-schema-2.1.0.json`). Structure is simple: `version`, `$schema`, `runs[]`,
each run has `tool.driver` (name, rules[]) and `results[]`
(ruleId, level, message, locations[].physicalLocation.region, partialFingerprints).
`partialFingerprints` is exactly what we need for de-duplication across rescans.

**Decision/impact:**
- Emit SARIF 2.1.0. Use `partialFingerprints` (hash of ruleId+file+line+snippet) as
  our dedup key. Low risk, high credibility (GitHub code scanning ingests SARIF).
- This is a real differentiator vs tools that only print text.

## 3. Local LLM PoC / test generation (THE differentiator + THE risk) — PARTIAL

This is what makes kwaro "mind-blowing" (proof, not opinion). It is also the
highest-risk claim.

**Verified concerns from research:**
- LLMs struggle with long-horizon, multi-step security tasks. Benchmarks
  (EXPLOITBENCH for V8 exploitation, SEC-bench Pro, ACL 2025 vuln-agent papers)
  show meaningful gaps in exploit/proof correctness.
- A 2025 study found ~40% of GitHub Copilot code completions were vulnerable,
  illustrating generation-quality risk generally.
- Generating a PoC that *actually compiles and reproduces* requires the model to
  understand build context, dependencies, and runtime, which local 7B-14B models
  do imperfectly.

**Decision/impact (how we de-risk it):**
- v1 = GENERATE the PoC/test file only; do NOT auto-execute by default. User reviews.
- When execution is enabled (opt-in, sandboxed temp dir, no network, no writes
  outside sandbox), treat a non-reproducing PoC as "unverified," not "confirmed."
  Never present a generated PoC as proof unless it runs and fails as expected.
- Quality improves with model size; recommend 14B+ for PoC generation. Smaller
  models may produce plausible-but-broken PoCs, so label confidence honestly.
- Combine with static analysis: the model explains/contextualizes findings the
  static checks already flagged, which is more reliable than pure generation.

## 4. Cross-OS, zero-dep, single-language — VERIFIED, low risk

Pure Python stdlib, `pathlib`, `subprocess` with list args, no compiled extensions.
Runs on Windows/macOS/Linux/WSL. This is the safe part of the plan; open-kritt's
pain (Prisma engine, esbuild per-OS) does not apply to us.

## 5. Free-first / offline — VERIFIED, strong position

Ollama runs fully offline, no key, no cyber-safety blocks. Paid providers (OpenAI,
Anthropic) may refuse security-research prompts; local models do not. This is both
a cost win and a reliability win for our exact use case.

## 6. Detection breadth vs incumbents — HONEST GAP

We will NOT match Semgrep/CodeQL/SAST tools on day one for raw rule coverage.
Those have years of tuning. Our edge is: free + local + agentic triage + PoC proof
+ any-domain via prompts. We should NOT claim "finds more than X." We claim
"free, local, proves findings, works on any code."

## Gaps to fix before/while building

1. **Tool-call robustness layer** (retry, malformed-JSON recovery, model-size
   gating). Build requirement.
2. **PoC verification honesty** (generate-only v1; executed PoCs marked unverified
   unless they run). Build requirement.
3. **Default model guidance** in `kwaro init` (recommend 14B-class for agent/PoC).
4. **Static-first pipeline** (model explains static findings, not pure generation)
   to keep false positives down.
5. **Trust/safety copy**: scans stay local; PoC execution is sandboxed + opt-in.
   State plainly to avoid adoption fear.
6. **Benchmark ourselves** on a known-vulnerable repo (e.g. DWVA/Juice Shop style
   fixtures) so we can show real recall in docs/README, not vibes.

## Verdict

The plan is technically sound and the differentiators (free/local, SARIF, PoC
proof, any-domain) are real and verifiable. The two risks, tool-call reliability
and PoC correctness, are manageable with the mitigations above. The biggest threat
to "mind-blowing + stars" is execution quality of the PoC layer, so we invest there
and we are honest about confidence.
