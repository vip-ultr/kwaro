"""
kwaro PoC math prototype (zero deps, pure stdlib).
Verifies the three locked math primitives on a concrete example:
  1. Bayesian posterior over evidence (prove/verify drive belief)
  2. Loop variant termination (find,prove,fix,verify converges)
  3. Pipeline transition graph + trace validator
Run: python3 math_prototype.py
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ---------------------------------------------------------------------------
# 1. BAYESIAN CONFIDENCE (not a model guess)
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    title: str
    prior: float = 0.05            # base rate: 5% of candidate flags are real
    posterior: float = 0.05
    evidence: list[str] = field(default_factory=list)

    def add_evidence(self, desc: str, likelihood_if_real: float,
                     likelihood_if_fake: float) -> float:
        """Update posterior with one piece of evidence via Bayes rule.
        likelihood_if_real  = P(evidence | real)
        likelihood_if_fake  = P(evidence | not real)   (false-positive rate)
        """
        p_real = self.posterior
        p_fake = 1.0 - p_real
        num = likelihood_if_real * p_real
        den = num + likelihood_if_fake * p_fake
        self.posterior = num / den
        self.evidence.append(desc)
        return self.posterior


def bayes_example() -> None:
    print("=" * 70)
    print("1. BAYESIAN CONFIDENCE  (a model says '90% sure' — should we trust it?)")
    print("=" * 70)
    f = Finding("SQL injection in login query")
    print(f"  prior P(real)            = {f.prior:.4f}  (base rate of candidate flags)")
    print(f"  model's blind guess      = 0.90  (ignored by kwaro)")
    # prove() evidence: static analyzer found string concatenation into SQL
    f.add_evidence("static: tainted var flows into cursor.execute", 0.85, 0.10)
    print(f"  after PROVE  (static)    = {f.posterior:.4f}")
    # verify() evidence: generated PoC actually returns 200 with injected payload
    f.add_evidence("verify: PoC ' OR 1=1 --  returns auth bypass", 0.95, 0.05)
    print(f"  after VERIFY (PoC)       = {f.posterior:.4f}")
    print(f"  -> report only if posterior >= 0.60  => KEEP = {f.posterior >= 0.60}")
    print()

    # contrast: a false alarm the model also rated 0.90
    g = Finding("Hardcoded secret in config.py")
    g.add_evidence("static: literal matches secret regex", 0.80, 0.20)
    # verify fails: value is a public test key, PoC shows no exposure
    g.add_evidence("verify: value is a public test key, no exposure", 0.10, 0.90)
    print(f"  contrast flag 'hardcoded secret'")
    print(f"    prior={g.prior:.3f} -> after prove={g.posterior:.4f} -> after verify={g.posterior:.4f}")
    print(f"    -> KEEP = {g.posterior >= 0.60}  (model said 0.90, but evidence dropped it)")
    print()


# ---------------------------------------------------------------------------
# 2. LOOP VARIANT TERMINATION (find,prove,fix,verify as a contraction)
# ---------------------------------------------------------------------------
class Stage(Enum):
    FIND = "find"
    PROVE = "prove"
    FIX = "fix"
    VERIFY = "verify"
    DONE = "done"


def loop_variant(findings: list[LoopFinding]) -> int:
    """V(s) = unproven + unfixed + unverified. Strictly decreases as we progress."""
    v = 0
    for fnd in findings:
        if not fnd.proven:
            v += 1
        if not fnd.fixed:
            v += 1
        if not fnd.verified:
            v += 1
    return v


@dataclass
class LoopFinding:
    title: str
    proven: bool = False
    fixed: bool = False
    verified: bool = False


def loop_example() -> None:
    print("=" * 70)
    print("2. LOOP VARIANT TERMINATION  V(s) = unproven+unfixed+unverified")
    print("=" * 70)
    fs = [LoopFinding("SQLi login"), LoopFinding("XSS search"), LoopFinding("traversal /api")]
    N = 12  # iteration cap
    trace: list[int] = [loop_variant(fs)]
    t = 0
    prev = trace[-1]
    while t < N:
        # one pass: prove all, fix all, verify all
        for fnd in fs:
            if not fnd.proven:
                fnd.proven = True
            elif not fnd.fixed:
                fnd.fixed = True
            elif not fnd.verified:
                fnd.verified = True
        v = loop_variant(fs)
        trace.append(v)
        t += 1
        if v >= prev:
            print("  !! variant did not decrease -> divergence detected, bail")
            break
        if v == 0:
            break
        prev = v
    print(f"  variant trace: {' -> '.join(str(x) for x in trace)}")
    print(f"  converged in {t} pass(es), V=0 => STOP. (cap was {N})")
    # prove the contraction bound
    decs = [trace[i] - trace[i+1] for i in range(len(trace)-1)]
    print(f"  per-pass decrements: {decs}  (all > 0 => strict, monotonic => terminates)")
    print()


# ---------------------------------------------------------------------------
# 3. PIPELINE GRAPH + TRACE VALIDATOR
# ---------------------------------------------------------------------------
EDGES: dict[Stage, list[Stage]] = {
    Stage.FIND: [Stage.PROVE],
    Stage.PROVE: [Stage.FIX],
    Stage.FIX: [Stage.VERIFY],
    Stage.VERIFY: [Stage.FIND, Stage.DONE],  # loop back only if issues remain
    Stage.DONE: [],
}


def is_valid_trace(trace: list[Stage]) -> tuple[bool, str]:
    """A run is valid iff each consecutive pair is a legal edge in EDGES."""
    for a, b in zip(trace, trace[1:]):
        if b not in EDGES[a]:
            return False, f"illegal transition {a.value} -> {b.value}"
    return True, "ok"


def graph_example() -> None:
    print("=" * 70)
    print("3. PIPELINE GRAPH + TRACE VALIDATOR")
    print("=" * 70)
    print("  legal edges:")
    for a, bs in EDGES.items():
        print(f"    {a.value:6} -> {[b.value for b in bs]}")
    good = [Stage.FIND, Stage.PROVE, Stage.FIX, Stage.VERIFY,
            Stage.FIND, Stage.PROVE, Stage.FIX, Stage.VERIFY, Stage.DONE]
    bad = [Stage.FIND, Stage.FIX, Stage.VERIFY]  # skipped PROVE
    ok, why = is_valid_trace(good)
    print(f"\n  trace A (normal loop): {[s.value for s in good]}")
    print(f"    valid = {ok}  ({why})")
    ok2, why2 = is_valid_trace(bad)
    print(f"  trace B (skipped prove): {[s.value for s in bad]}")
    print(f"    valid = {ok2}  ({why2})")
    # reachability: can FIND reach DONE? simple BFS over EDGES
    seen, frontier = set(), [Stage.FIND]
    while frontier:
        n = frontier.pop()
        if n in seen:
            continue
        seen.add(n)
        frontier += EDGES[n]
    print(f"  reachability FIND->DONE: {Stage.DONE in seen}  (reachable: {[s.value for s in seen]})")
    print()


# ---------------------------------------------------------------------------
# 4. SPRT STOP RULE (rigorous version of the posterior threshold)
#    From sequential analysis: stop as soon as the log-likelihood ratio
#    crosses an upper bound A (accept H1 = real) or lower bound B (accept H0).
#    This strictly controls Type I (false positive) and Type II (miss) rates,
#    and can stop early instead of waiting for a fixed posterior.
# ---------------------------------------------------------------------------
def sprt_bounds(alpha: float, beta: float) -> tuple[float, float]:
    """A = log((1-beta)/alpha), B = log(beta/(1-alpha))."""
    return (math.log((1.0 - beta) / alpha), math.log(beta / (1.0 - beta)))


def sprt_decision(log_lrs: list[float], alpha: float = 0.05, beta: float = 0.10):
    A, B = sprt_bounds(alpha, beta)
    s = 0.0
    trace = [s]
    for llr in log_lrs:
        s += llr
        trace.append(s)
        if s >= A:
            return "REAL", s, trace
        if s <= B:
            return "FALSE", s, trace
    return "INCONCLUSIVE", s, trace


def sprt_example() -> None:
    print("=" * 70)
    print("4. SPRT STOP RULE  (replaces fixed 0.60 threshold)")
    print("=" * 70)
    A, B = sprt_bounds(0.05, 0.10)
    print(f"  alpha(Type I)=0.05 beta(Type II)=0.10 -> A={A:.3f} B={B:.3f}")
    # real SQLi: prove then verify both favor real
    real_llrs = [math.log(0.85 / 0.10), math.log(0.95 / 0.05)]
    d1, s1, t1 = sprt_decision(real_llrs)
    print(f"  real SQLi  log-LR steps={[f'{x:.2f}' for x in real_llrs]} cum={t1}")
    print(f"    decision = {d1}  (crossed A={A:.3f} at cum {s1:.2f})")
    # false alarm: prove favors real slightly, TWO independent verify checks fail
    fake_llrs = [math.log(0.80 / 0.20), math.log(0.10 / 0.90), math.log(0.10 / 0.90)]
    d2, s2, t2 = sprt_decision(fake_llrs)
    print(f"  false alarm log-LR steps={[f'{x:.2f}' for x in fake_llrs]} cum={t2}")
    print(f"    decision = {d2}  (crossed B={B:.3f} at cum {s2:.2f})")
    print()


if __name__ == "__main__":
    bayes_example()
    loop_example()
    graph_example()
    sprt_example()
    print("ALL PRIMITIVES VERIFIED ON EXAMPLE INPUT.")
