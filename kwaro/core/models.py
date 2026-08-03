"""kwaro core: shared data models.

Finding and Scan carry both the security schema (L7) and the math fields locked
in docs/math.md, so the report can show the evidence-driven confidence, the
SPRT verdict, the pipeline stage, and the loop-variant trace.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(str, Enum):
    LOW = "low"
    MED = "med"
    HIGH = "high"


class PocState(str, Enum):
    NONE = "none"
    GENERATED = "generated"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


class SprtDecision(str, Enum):
    NONE = "none"
    REAL = "real"
    FALSE = "false"
    INCONCLUSIVE = "inconclusive"


class Stage(str, Enum):
    """Pipeline graph nodes (docs/math.md Primitive 3)."""
    FIND = "find"
    PROVE = "prove"
    FIX = "fix"
    VERIFY = "verify"
    DONE = "done"


@dataclass
class Evidence:
    """One prove/verify check feeding the Bayesian update and SPRT log-LR."""
    desc: str
    l_real: float   # P(evidence | real)
    l_fake: float   # P(evidence | fake)
    llr: float = 0.0  # log(l_real / l_fake), filled by verify.update

    def __post_init__(self) -> None:
        if self.llr == 0.0 and self.l_real > 0 and self.l_fake > 0:
            self.llr = math.log(self.l_real / self.l_fake)


import math  # noqa: E402  (kept after Evidence to avoid circular import noise)


@dataclass
class Finding:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    scan_id: str = ""
    title: str = ""
    severity: Severity = Severity.MEDIUM
    cwe: str = ""
    rule_id: str = ""
    source: str = "static"  # static | model | static+model
    confidence: Confidence = Confidence.LOW
    file: str = ""
    line_start: int = 0
    line_end: int = 0
    column: int = 0
    snippet: str = ""
    description: str = ""
    suggested_fix: str = ""
    poc_path: str = ""
    poc_state: PocState = PocState.NONE
    fingerprint: str = ""
    created_at: float = field(default_factory=time.time)

    # ---- MATH FIELDS (locked in docs/math.md, L7) ----
    prior: float = 0.05
    posterior: float = 0.05
    evidence: list = field(default_factory=list)  # list[Evidence]
    sprt_alpha: float = 0.05
    sprt_beta: float = 0.10
    sprt_decision: SprtDecision = SprtDecision.NONE
    stage: Stage = Stage.FIND
    loop_variant: list = field(default_factory=list)  # V(s) trace

    def add_evidence(self, desc: str, l_real: float, l_fake: float) -> Evidence:
        """Append a prove/verify check and return it (caller runs verify.update)."""
        ev = Evidence(desc=desc, l_real=l_real, l_fake=l_fake)
        self.evidence.append(ev)
        return ev

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "title": self.title,
            "severity": self.severity.value,
            "cwe": self.cwe,
            "rule_id": self.rule_id,
            "source": self.source,
            "confidence": self.confidence.value,
            "file": self.file,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column": self.column,
            "snippet": self.snippet,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "poc_path": self.poc_path,
            "poc_state": self.poc_state.value,
            "fingerprint": self.fingerprint,
            "created_at": self.created_at,
            "prior": self.prior,
            "posterior": self.posterior,
            "evidence": [vars(e) for e in self.evidence],
            "sprt_alpha": self.sprt_alpha,
            "sprt_beta": self.sprt_beta,
            "sprt_decision": self.sprt_decision.value,
            "stage": self.stage.value,
            "loop_variant": self.loop_variant,
        }

    @classmethod
    def from_row(cls, row: dict) -> "Finding":
        f = cls(
            id=row["id"], scan_id=row.get("scan_id", ""), title=row.get("title", ""),
            severity=Severity(row["severity"]), cwe=row.get("cwe", ""),
            rule_id=row.get("rule_id", ""), source=row.get("source", "static"),
            confidence=Confidence(row["confidence"]), file=row.get("file", ""),
            line_start=row.get("line_start", 0), line_end=row.get("line_end", 0),
            column=row.get("column", 0), snippet=row.get("snippet", ""),
            description=row.get("description", ""), suggested_fix=row.get("suggested_fix", ""),
            poc_path=row.get("poc_path", ""), poc_state=PocState(row["poc_state"]),
            fingerprint=row.get("fingerprint", ""),
            prior=row.get("prior", 0.05), posterior=row.get("posterior", 0.05),
            sprt_alpha=row.get("sprt_alpha", 0.05), sprt_beta=row.get("sprt_beta", 0.10),
            sprt_decision=SprtDecision(row.get("sprt_decision", "none")),
            stage=Stage(row.get("stage", "find")),
        )
        raw_ev = row.get("evidence")
        if raw_ev:
            f.evidence = [Evidence(**e) for e in json.loads(raw_ev)] if isinstance(raw_ev, str) else [Evidence(**e) for e in raw_ev]
        raw_lv = row.get("loop_variant")
        if raw_lv:
            f.loop_variant = json.loads(raw_lv) if isinstance(raw_lv, str) else raw_lv
        return f


@dataclass
class Scan:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target: str = ""
    target_type: str = "local"  # local | git
    commit: str = ""
    provider: str = ""
    model: str = ""
    profile: str = "generic"
    status: str = "running"  # running | done | failed
    started_at: float = field(default_factory=time.time)
    finished_at: float = 0.0
    finding_count: int = 0
    precision: Optional[float] = None
    recall: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id, "target": self.target, "target_type": self.target_type,
            "commit": self.commit, "provider": self.provider, "model": self.model,
            "profile": self.profile, "status": self.status,
            "started_at": self.started_at, "finished_at": self.finished_at,
            "finding_count": self.finding_count, "precision": self.precision,
            "recall": self.recall,
        }
