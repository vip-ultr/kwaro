"""kwaro core: ranking + de-duplication (locked decisions L3, L4).

L3 - Severity = CVSS-style bands + composite confidence:
  Bands: Critical 9.0-10, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9, Info <0.1.
  Composite signal raises/lowers confidence (not band alone):
  static-confirmed > model-only; PoC VERIFIED > UNVERIFIED.

L4 - De-duplication by ROOT CAUSE:
  Dedup key = ruleId + normalized file + normalized line + normalized snippet hash.
  Findings merge by root cause, not tool output.
"""
from __future__ import annotations

import hashlib
from typing import List

from .models import Finding, Severity, Confidence, PocState


# --- L3: severity bands (qualitative CVSS-style) ---
BANDS = {
    Severity.CRITICAL: (9.0, 10.0),
    Severity.HIGH: (7.0, 8.9),
    Severity.MEDIUM: (4.0, 6.9),
    Severity.LOW: (0.1, 3.9),
    Severity.INFO: (0.0, 0.09),
}


def severity_score(sev: Severity) -> float:
    """Midpoint of the band (qualitative; not a precise CVSS vector)."""
    lo, hi = BANDS.get(sev, (0.0, 0.09))
    return round((lo + hi) / 2.0, 2)


_SOURCE_WEIGHT = {
    "static": 0.60,
    "model": 0.40,
    "static+model": 0.70,
}


def composite_confidence(f: Finding) -> float:
    """L3 composite confidence in [0, 1].

    Combines the Bayesian posterior (math spine) with source strength and PoC
    state. Higher = more certain the finding is real. Never claims precision;
    it is a transparent heuristic behind the report's confidence.
    """
    posterior = max(0.0, min(1.0, f.posterior))
    source_w = _SOURCE_WEIGHT.get(f.source, 0.40)
    # blend posterior (the evidence-driven belief) with source strength
    conf = posterior * 0.7 + source_w * 0.3
    # PoC boosts confidence; VERIFIED > UNVERIFIED (L6: UNVERIFIED never raises severity)
    if f.poc_state == PocState.VERIFIED:
        conf = min(1.0, conf + 0.20)
    elif f.poc_state == PocState.UNVERIFIED or f.poc_state == PocState.GENERATED:
        conf = min(1.0, conf + 0.05)
    # a few corroborating evidence items nudge confidence up slightly
    conf = min(1.0, conf + 0.01 * max(0, len(f.evidence) - 1))
    return round(conf, 3)


def confidence_label(conf: float) -> Confidence:
    if conf >= 0.66:
        return Confidence.HIGH
    if conf >= 0.33:
        return Confidence.MED
    return Confidence.LOW


# --- L4: root-cause fingerprint ---
def fingerprint(f: Finding) -> str:
    """Dedup key = ruleId + norm file + norm line + snippet hash (L4)."""
    norm_file = (f.file or "").replace("\\", "/").lower().strip("/")
    norm_snip = "".join((f.snippet or "").lower().split())
    snip_hash = hashlib.sha1(norm_snip.encode("utf-8", "ignore")).hexdigest()[:12]
    raw = f"{f.rule_id}|{norm_file}|{f.line_start}|{snip_hash}"
    return hashlib.sha1(raw.encode("utf-8", "ignore")).hexdigest()[:16]


def dedup_by_root_cause(findings: List[Finding]) -> List[Finding]:
    """Merge findings by root cause (L4). First occurrence wins; we keep its data."""
    seen = {}
    out: List[Finding] = []
    for f in findings:
        key = fingerprint(f)
        if key not in seen:
            f.fingerprint = key
            seen[key] = f
            out.append(f)
    return out


def rank(findings: List[Finding]) -> List[Finding]:
    """Sort by severity band (desc), then composite confidence (desc)."""
    return sorted(
        findings,
        key=lambda f: (BANDS[f.severity][1], composite_confidence(f)),
        reverse=True,
    )
