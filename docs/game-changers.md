# kwaro - Game-Changer Features

What makes kwaro "mind-blowing" versus incumbents. The locked engine (find + prove)
is table stakes for us; these are the differentiators that earn stars. Each is
feasible on our free, local, zero-dep stack. Ranked by impact.

## GC1. Find -> Prove -> Fix -> Verify closed loop (THE headline)
Most tools stop at "here is a bug." kwaro goes further, all locally:
1. **Find** via static + model triage.
2. **Prove** by generating AND running a PoC in a sandbox, showing the actual crash.
3. **Fix** via the chat agent that edits the file with a real remediation.
4. **Verify** by re-scanning the changed file to confirm the finding is gone.
The user watches a vulnerability go from "reported" to "proven" to "fixed and
verified" in one session, on their own machine, for free. Nobody free does the full
loop. This is the demo that goes viral.

## GC2. Privacy as a first-class feature, not a footnote
"We never upload your code. Ever." Local models mean zero network for analysis.
For fintech/banking/blockchain teams, cloud scanners (Snyk, SaaS SAST) are a
compliance blocker. kwaro turns "can't use cloud scanning" into "use kwaro, locally."
Market this hard; it is a real, defensible moat incumbents structurally can't match.

## GC3. Reproduce button on every finding
One command/click: `kwaro prove <finding-id>` generates and runs a PoC, returns the
crash output. Turns a report line into undeniable evidence. Security teams use this
to convince engineers to fix; managers use it to show risk. Tangible, shareable proof.

## GC4. Conversational, codebase-aware remediation
Not "fix it yourself." The chat agent reads your actual code, proposes a patch,
applies it, and re-scans to confirm. "Why is this a problem for MY app?" gets a
plain-language answer using the model, not generic CWE boilerplate. Lowerers the
barrier from "I have 40 findings" to "kwaro fixed 12 of them just now."

## GC5. Community domain profiles (growth loop)
Scan behavior is driven by profiles (fintech, blockchain/Solidity, AI-app, plus a
generic default). Profiles are plain prompt+rule files in the repo. Anyone can
write one and PR it. This turns users into contributors and creates a library of
expert scanners no single vendor would fund. Open-source virality by design.

## GC6. Honest confidence on every finding
Each finding shows its evidence chain: static rule hit? model confirmation? PoC
verified? confidence level. Users trust kwaro because it tells them what it KNOWS vs
what it GUESSES. Incumbents hide this; we make it the UI's centerpiece. Trust = adoption.

## GC7. PR / pre-commit guard with SARIF
`kwaro scan --diff` checks only changed files; outputs SARIF for GitHub code scanning
and a human summary for the terminal. Drop into CI or a pre-commit hook. Free, local,
no per-seat SaaS. Catches regressions before merge, not after.

## GC8. Explain-like-a-human
Every finding gets a one-paragraph "why this matters here" generated from the model
reading the surrounding code, not a CWE description copy-paste. Makes security
findings readable to non-security devs. Adoption driver inside teams.

## What we deliberately DO NOT do (scope discipline)
- No claim of beating Semgrep/CodeQL on raw rule coverage. We win on free + local +
  proof + any-domain + fix loop.
- No hardcoded named agents (option A). No competitor names in product.
- No React/Node build in v1. No Docker requirement to run.

## Priority for build
GC1 (closed loop) and GC3 (reproduce) are the viral core -> build first, demo early.
GC2/GC6 are messaging + UI treatment. GC4/GC5/GC7/GC8 are fast follow-ons that
compound the loop. GC5 (community profiles) is the long-term growth engine.
