"""kwaro core: pipeline (explicit FIND/PROVE/FIX/VERIFY steps + aggregate + rank).

This wraps the Phase 1 math spine (loop variant, graph, Bayes/SPRT) into named
pipeline STAGES (docs/agents.md) and adds Phase 4 work: aggregate findings, de-dupe
by root cause (L4), assign composite confidence + severity ranking (L3). It does
NOT replace the math; it orchestrates it and reports on it.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

from . import graph, loop, verify
from .models import Finding, Scan, SprtDecision, Stage
from .rank import dedup_by_root_cause, rank, composite_confidence, fingerprint


def run_pipeline(
    findings: List[Finding],
    prove: Callable[[Finding], None],
    fix: Callable[[Finding], None],
    verify_finding: Callable[[Finding], None],
    cap: int = 12,
    generate_pocs: bool = False,
    poc_dir: Optional[str] = None,
    provider=None,
) -> dict:
    """Execute the bounded find, prove, fix, verify loop, then aggregate + rank.

    Returns a result dict with: trace (loop variant), graph_valid, graph_why,
    unique (de-duped findings), ranked (sorted), kept (posterior>=0.5 or SPRT REAL).
    """
    # Stage: PROVE -> FIX -> VERIFY over each candidate (Phase 1 math spine, Primitive 2)
    trace = loop.run(findings, prove, fix, verify_finding, cap=cap)

    # Stage: aggregate + de-dupe by root cause (L4)
    for f in findings:
        f.fingerprint = fingerprint(f)
    unique = dedup_by_root_cause(findings)

    # Stage: rank (L3 composite confidence + severity bands)
    ranked = rank(unique)

    # Stage: VERIFY graph trace validity (Primitive 3)
    last = Stage.DONE if not findings else Stage.FIND
    valid, why = graph.is_valid_trace(
        [Stage.FIND, Stage.PROVE, Stage.FIX, Stage.VERIFY, last]
    )

    # Stage: optional PoC generation (L6: generate-only, never executes)
    if generate_pocs:
        from ..analyzers.prover import generate_poc
        for f in ranked:
            generate_poc(f, poc_dir or os.path.join(os.getcwd(), "kwaro_pocs"), provider)

    kept = [f for f in ranked if f.sprt_decision == SprtDecision.REAL or f.posterior >= 0.5]
    return {
        "trace": trace,
        "graph_valid": valid,
        "graph_why": why,
        "unique": unique,
        "ranked": ranked,
        "kept": kept,
    }


def attach_scan_math(scan: Scan, result: dict) -> None:
    """Compute scan-level precision/recall framing (docs/math.md ranking framing).

    With no ground-truth labels this scan, we surface the kept/total ratio as a
    transparent signal and leave precision/recall null until an eval set exists (L13).
    """
    total = len(result["unique"])
    kept = len(result["kept"])
    scan.finding_count = total
    scan.kept_count = kept
    # precision/recall stay null (L7): set only when an eval ground truth is provided.
