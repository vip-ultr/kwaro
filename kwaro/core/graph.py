"""kwaro core: pipeline graph (state machine + trace validator).

Implements docs/math.md Primitive 3. The find, prove, fix, verify pipeline is a
directed graph. VERIFY loops back to FIND only if issues remain. PROVE can never
be skipped. A completed run is a trace; validate_trace rejects illegal walks.
Pure stdlib, zero deps.
"""
from __future__ import annotations

from typing import List

from .models import Stage


EDGES = {
    Stage.FIND: [Stage.PROVE],
    Stage.PROVE: [Stage.FIX],
    Stage.FIX: [Stage.VERIFY],
    Stage.VERIFY: [Stage.FIND, Stage.DONE],
    Stage.DONE: [],
}


def legal_next(stage: Stage) -> List[Stage]:
    return EDGES[stage]


def is_valid_trace(trace: List[Stage]) -> tuple[bool, str]:
    """A run is valid iff each consecutive pair is a legal edge in EDGES."""
    if not trace:
        return False, "empty trace"
    for a, b in zip(trace, trace[1:]):
        if b not in EDGES[a]:
            return False, f"illegal transition {a.value} -> {b.value}"
    return True, "ok"


def reachable(start: Stage, goal: Stage) -> bool:
    """BFS over EDGES: can start reach goal?"""
    seen, frontier = set(), [start]
    while frontier:
        n = frontier.pop()
        if n in seen:
            continue
        seen.add(n)
        frontier.extend(EDGES[n])
    return goal in seen


def advance(stage: Stage, issues_remain: bool) -> Stage:
    """Compute the next stage from VERIFY given whether issues remain."""
    if stage == Stage.VERIFY:
        return Stage.FIND if issues_remain else Stage.DONE
    nxt = EDGES[stage]
    return nxt[0]
