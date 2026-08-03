# kwaro - The Math (locked primitives)

This document is the source of truth for the math that makes kwaro different
from a normal "scan and guess" tool. It is kept up to date as we verify and
improve each primitive. Every formula here has been run on a concrete example
(see `experiments/math_prototype.py`) and the real output is pasted below.

Why this exists: the security-tool space is full of scanners that output a
model's confidence number and call it a day. kwaro's differentiator is that
confidence and termination are DERIVED from the find, prove, fix, verify loop,
not asserted by the model. These three primitives make that explicit and
honest. All are pure stdlib Python, zero runtime deps, offline-friendly.

---

## Primitive 1: Bayesian confidence (not a model guess)

A finding's belief is updated by evidence collected in the prove and verify
stages, using Bayes rule:

    P(real | evidence) = P(evidence | real) * P(real)
                          ---------------------------------
                          P(evidence | real)*P(real) + P(evidence | fake)*P(fake)

We start from a low base rate (candidate flags are mostly noise):

    prior P(real) = 0.05

Each evidence item e_i updates the posterior:

    posterior_{n+1} = L_real(e_{n+1}) * posterior_n
                      ------------------------------------------------
                      L_real(e_{n+1})*posterior_n + L_fake(e_{n+1})*(1-posterior_n)

where L_real = P(evidence | real), L_fake = P(evidence | fake).

A finding is only reported if its final posterior crosses a threshold
(0.60 in the prototype). The model's own "I'm 90% sure" number is IGNORED.

### Verified example (real output)

    prior P(real)            = 0.0500   (base rate of candidate flags)
    model's blind guess      = 0.90     (ignored by kwaro)
    after PROVE  (static)    = 0.3091
    after VERIFY (PoC)       = 0.8947
    -> report only if posterior >= 0.60 => KEEP = True

    contrast flag 'hardcoded secret'
      prior=0.050 -> after prove=0.0229 -> after verify=0.0229
      -> KEEP = False  (model said 0.90, but evidence dropped it)

What this proves: a real SQLi climbs from 0.05 to 0.89 as static + PoC evidence
arrives. A false alarm the model also rated 0.90 collapses to 0.02 because the
verify stage found no real exposure. The math, not the model, decides.

---

## Primitive 2: Loop variant termination

The run state s_t has a variant:

    V(s_t) = |unproven| + |unfixed| + |unverified|

The loop is a contraction if V strictly decreases and is bounded below by 0:

    V(s_{t+1}) < V(s_t),   V(s_t) >= 0,   t <= N   (N = iteration cap)

When V = 0, all findings are proven, fixed, and verified, so the loop stops.
The iteration cap N is the safety net: if V is not converging, bail instead of
running forever. We also detect divergence if V does not decrease in a pass.

This is fixed-point iteration: the verified end state s* is the fixed point
V(s*) = 0. Banach-style convergence is implied by the strict monotonic decrease.

### Verified example (real output)

    variant trace: 9 -> 6 -> 3 -> 0
    converged in 3 pass(es), V=0 => STOP. (cap was 12)
    per-pass decrements: [3, 3, 3]  (all > 0 => strict, monotonic => terminates)

What this proves: with 3 findings (9 units of work), each pass proves, fixes,
and verifies one stage for all, driving V down by 3 every time, hitting 0 in 3
passes. The loop is provably terminating and the variant is visible in output.

---

## Primitive 3: Pipeline graph + trace validator

The find, prove, fix, verify pipeline is a directed graph
G = (V, E). V = {find, prove, fix, verify, done}. E is locked:

    find   -> prove
    prove  -> fix
    fix    -> verify
    verify -> find | done      (loop back ONLY if issues remain)
    done   -> (none)

A completed run produces a trace tau = (v_1, a_1, v_2, ...). The trace is valid
iff every consecutive pair is a legal edge. This gives tamper-evident lineage:
you can re-validate any saved run by checking tau is a walk in G. Reachability
from find to done is decidable by BFS over E (no skipped stages allowed).

### Verified example (real output)

    trace A (normal loop): [find, prove, fix, verify, find, prove, fix, verify, done]
      valid = True  (ok)
    trace B (skipped prove): [find, fix, verify]
      valid = False  (illegal transition find -> fix)
    reachability FIND->DONE: True  (reachable: [done, prove, fix, find, verify])

What this proves: a run that skips the prove stage is rejected by the validator.
Every reported run is a legal walk, so findings always carry full lineage.

---

## How these combine

- Primitive 2 (variant) is the spine: it drives the loop and proves termination.
- Primitive 1 (Bayes) is what happens INSIDE the prove/verify nodes: it decides
  whether a candidate survives to the report.
- Primitive 3 (graph) is the skeleton: it enforces that prove can never be
  skipped, so Primitive 1 always has real evidence to work with.

Together they make kwaro's headline true and verifiable: "it doesn't just guess,
it proves, fixes, and verifies, and shows you the math."

## Honest limits (state these in copy)

- Priors start uniform (0.05 base rate). They are tunable, not ground truth.
- Likelihoods (L_real, L_fake) come from deterministic checks in prove/verify,
  not from the model's feelings. So this is honest math, not vibes as probability.
- The loop variant assumes one stage advances per pass. If a stage can partially
  complete, V still decreases but may need finer granularity (future work).

---

## Primitive 4: SPRT stop rule (rigorous version of the threshold)

Primitive 1 uses a fixed posterior cutoff (0.60). Research into sequential
analysis (Wald's Sequential Probability Ratio Test, 1947) shows the theoretically
correct stop rule: accumulate the log-likelihood ratio and stop as soon as it
crosses an upper bound A (accept "real") or a lower bound B (accept "false"):

    LLR_n = sum_i log( L_real(e_i) / L_fake(e_i) )
    stop when LLR_n >= A  (decide real)   or  LLR_n <= B  (decide false)

Bounds are set from the error budget:

    A = log((1 - beta) / alpha),   B = log(beta / (1 - alpha))

where alpha = Type I rate (false positive) and beta = Type II rate (missed
finding). This strictly controls both error rates BY DESIGN and can stop early
instead of waiting for a fixed number of evidence items. It generalizes Primitive 1:
a posterior crossing 0.60 is just a special case of SPRT with a particular bound.

### Verified example (real output)

    alpha(Type I)=0.05 beta(Type II)=0.10 -> A=2.890 B=-2.197
    real SQLi  log-LR steps=['2.14', '2.94'] cum=[0.0, 2.14, 5.08]
      decision = REAL  (crossed A=2.890 at cum 5.08)
    false alarm log-LR steps=['1.39', '-2.20', '-2.20'] cum=[0.0, 1.39, -0.81, -3.01]
      decision = FALSE  (crossed B=-2.197 at cum -3.01)

What this proves: the real SQLi accumulates positive log-LR and crosses A after
the PoC. The false alarm's verify steps push LLR negative and cross B, so it is
rejected with a controlled false-positive rate. No magic 0.60 number needed.

---

## Research findings (are we doing the right thing?)

We checked the literature before locking these primitives. Summary:

1. **Bayesian / sequential updating is a real, proven pattern.** The BLF
   forecasting paper (Murphy, 2026) uses sequential Bayesian belief updates in an
   agent loop and beats top methods. Our Primitive 1 is the same shape, but we use
   EXPLICIT likelihoods from deterministic checks (not an LLM forward pass), which
   the BLF paper itself notes is the more principled approach. So we are on solid
   ground, and arguably more honest than the LLM-update version.
   CAVEAT from that paper: an LLM "Bayesian-style" update can violate proper
   Bayesian consistency. We avoid that by computing exact posteriors from
   likelihoods, not asking the model to update its own belief.

2. **Loop termination via a well-founded variant is standard theory.** Dershowitz
   (1979), the well-founded-relations literature, and fstar/lean all prove program
   termination with a measure that strictly decreases over a well-founded order.
   Our V(s) is exactly that measure. So Primitive 2 is textbook-correct, and the
   iteration cap N is the standard safety overlay.

3. **The pipeline graph is a transition system.** State machines + trace
   validation are the basis of workflow engines and formal verification (model
   checking). Primitive 3 is a minimal, correct instance. For deeper guarantees we
   could borrow model-checking later (reachability is already proven decidable).

4. **SPRT (Primitive 4) is the rigorous form of our stop rule.** We found this
   only after research; it replaces the ad-hoc 0.60 cutoff with error-rate
   guarantees. This is the single most important addition from the literature.

5. **MISSED before research: we had no principled stop rule and no ranking
   metric.** Two gaps closed: SPRT (stop) and the precision/recall framing below.

### Ranking / detection-quality framing (the metric we were missing)

A scanner's job is a ranked-retrieval problem (like search). We should report and
track, per scan and over time:

    precision = TP / (TP + FP)        (of reported findings, how many real)
    recall    = TP / (TP + FN)        (of real bugs, how many found)
    F_beta    = (1 + beta^2) * precision * recall / (beta^2*precision + recall)

For a security scanner, precision usually matters more than recall (a flood of
false positives gets ignored). SPRT directly optimizes the FP rate (alpha), so it
pushes precision up. We will expose precision/recall per scan in the report and
track them as the product's headline quality metric, not raw "findings found".

### What we deliberately are NOT claiming

- We are NOT doing full formal verification (theorem proving / model checking of
  the target code). That is a different, much heavier field (Tihanyi et al. 2025
  survey). kwaro is hybrid: deterministic static checks + model triage + SPRT-gated
  proof. We say "proves a finding with evidence", not "formally verifies your code".
  Staying honest here matters for credibility.

---

## Are we doing the right thing? Verdict

Yes, with two upgrades now locked: (a) replace the fixed 0.60 cutoff with SPRT
(Primitive 4), and (b) report precision/recall per scan as the quality metric.
The three originals (Bayes, variant, graph) are all textbook-correct and map
directly onto established theory. The combination (prove-driven belief + terminating
loop + auditable graph + SPRT stop + precision/recall reporting) is not something
off-the-shelf scanners expose with visible, evidence-driven confidence and an SPRT
error budget. The software is free and open-source and runs locally on the user's
own machine. Out of the box it works with a local model (Ollama) that needs no API
key and no internet. Users who want a stronger hosted model can bring their own API
key for a paid provider (opt-in, they pay the provider, not kwaro). All of the math
above is pure stdlib, zero-dep, and offline-capable regardless of which model backs it.

## Status

- [x] Bayesian confidence - prototyped and verified, and wired into core/verify.py + core/models.py
- [x] Loop variant termination - prototyped and verified, and wired into core/loop.py
- [x] Pipeline graph + trace validator - prototyped and verified, and wired into core/graph.py
- [x] SPRT stop rule - prototyped and verified (added 2026-08-03 from research), wired into core/verify.py
- [x] Wire into core/models.py, core/loop.py, core/graph.py, core/verify.py (Phase 1, shipped 2026-08-03)
- [x] pytest coverage for each primitive - tests/test_scan_math.py (4 tests pass, plus per-module checks)
- [ ] Precision/recall tracking per scan - schema field exists (Scan.precision/recall), not yet computed at scan end
- [ ] Expose variant + posterior + SPRT decision + precision/recall in the terminal/browser report UI

## Update log

- 2026-08-03: initial primitives (Bayes, variant, graph) prototyped and verified
  against experiments/math_prototype.py; real output captured.
- 2026-08-03: research pass. Added SPRT stop rule (Primitive 4) after finding the
  fixed 0.60 cutoff was ad-hoc; added precision/recall quality framing; documented
  the honest limit vs full formal verification. All four primitives re-verified on
  example input.
- 2026-08-03: Phase 1 shipped. All four primitives implemented in core/ (verify,
  loop, graph, models) and exercised end-to-end by `kwaro scan` on a fixture;
  persisted to SQLite; covered by pytest.
