"""kwaro core: bounded find, prove, fix, verify loop.

Implements docs/math.md Primitive 2 (loop variant termination). The run state's
variant V(s) = number of findings not yet at DONE. Each pass advances findings
one stage (find -> prove -> fix -> verify). A finding that clears the belief bar
in verify_finding is marked DONE and drops out of the variant. The loop stops at
V == 0, at the iteration cap N, or on divergence (V not strictly decreasing while
work happened).

The loop is provider-agnostic: callables for prove/fix/verify are injected, so
the same spine works with static-only, Ollama, or any BYOK provider. Pure stdlib.
"""
from __future__ import annotations

from typing import Callable, List

from .models import Finding, Stage


def loop_variant(findings: List[Finding]) -> int:
    """V(s) = number of findings not yet at DONE."""
    return sum(1 for f in findings if f.stage != Stage.DONE)


def run(
    findings: List[Finding],
    prove: Callable[[Finding], None],
    fix: Callable[[Finding], None],
    verify: Callable[[Finding], None],
    cap: int = 12,
) -> List[int]:
    """Drive findings through the loop. Returns the V(s) trace (for the report)."""
    trace: List[int] = [loop_variant(findings)]
    prev = trace[-1]
    for _ in range(cap):
        progressed = False
        for f in findings:
            if f.stage == Stage.FIND:
                prove(f); f.stage = Stage.PROVE; progressed = True
            elif f.stage == Stage.PROVE:
                fix(f); f.stage = Stage.FIX; progressed = True
            elif f.stage == Stage.FIX:
                verify(f)  # may set stage to DONE or leave at VERIFY
                progressed = True
        v = loop_variant(findings)
        trace.append(v)
        if v >= prev and progressed:
            break  # divergence: work happened but variant did not decrease
        if v == 0:
            break
        prev = v
    return trace
