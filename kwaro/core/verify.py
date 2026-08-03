"""kwaro core: verify (Bayesian belief update + SPRT stop rule).

Implements docs/math.md Primitive 1 (sequential Bayesian confidence) and
Primitive 4 (SPRT stop rule). Pure stdlib, zero deps. Likelihoods come from
deterministic prove/verify checks, never from a model's self-reported confidence.
"""
from __future__ import annotations

import math
from typing import List, Tuple

from .models import Evidence, Finding, SprtDecision


def bayes_update(finding: Finding, desc: str, l_real: float, l_fake: float) -> float:
    """Add one piece of evidence and return the new posterior P(real | evidence).

    posterior_{n+1} = l_real * p / (l_real * p + l_fake * (1 - p))
    where p = current posterior.
    """
    p = finding.posterior
    num = l_real * p
    den = num + l_fake * (1.0 - p)
    finding.posterior = num / den if den > 0 else p
    finding.add_evidence(desc, l_real, l_fake)
    return finding.posterior


def sprt_bounds(alpha: float, beta: float) -> Tuple[float, float]:
    """A = log((1 - beta) / alpha), B = log(beta / (1 - alpha))."""
    return (math.log((1.0 - beta) / alpha), math.log(beta / (1.0 - alpha)))


def sprt_decision(evidence: List[Evidence], alpha: float = 0.05,
                  beta: float = 0.10) -> Tuple[SprtDecision, float]:
    """Accumulate log-LR over evidence; stop at upper (REAL) or lower (FALSE) bound.

    Returns (decision, cumulative_log_lr). If neither bound is crossed, the
    decision is INCONCLUSIVE (caller keeps collecting evidence or falls back).
    """
    A, B = sprt_bounds(alpha, beta)
    s = 0.0
    for ev in evidence:
        llr = ev.llr if ev.llr != 0.0 else math.log(ev.l_real / ev.l_fake)
        s += llr
        if s >= A:
            return SprtDecision.REAL, s
        if s <= B:
            return SprtDecision.FALSE, s
    return SprtDecision.INCONCLUSIVE, s


def evaluate(finding: Finding) -> Finding:
    """Run the full verify pass for a finding: Bayesian update already applied via
    bayes_update; here we compute the SPRT verdict. Mutates and returns finding."""
    if finding.evidence:
        finding.sprt_decision, _ = sprt_decision(
            finding.evidence, finding.sprt_alpha, finding.sprt_beta)
    return finding
