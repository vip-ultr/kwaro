"""kwaro core: export findings (SARIF 2.1.0 + JSON, zero-dep).

Emits the L7 fields plus the math fields so downstream tooling and the user can
see the evidence-driven confidence. SARIF uses `properties` for kwaro-specific
math (posterior, sprt_decision, fingerprint, confidence) so it stays valid for
generic SARIF viewers while carrying our signal.
"""
from __future__ import annotations

import json
from typing import List

from .models import Finding, Scan
from .rank import severity_score, composite_confidence


_SEVERITY_LEVEL = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "note",
}


def _result(f: Finding) -> dict:
    return {
        "ruleId": f.rule_id,
        "level": _SEVERITY_LEVEL.get(f.severity.value, "warning"),
        "message": {"text": f"{f.title}: {f.description}"},
        "locations": [{
            "physicalLocation": {
                "artifactLocation": {"uri": f.file},
                "region": {
                    "startLine": f.line_start,
                    "endLine": f.line_end or f.line_start,
                    "snippet": {"text": f.snippet or ""},
                },
            }
        }],
        "partialFingerprints": {"kwaro/rootCause": f.fingerprint or ""},
        "properties": {
            "cwe": f.cwe,
            "severity": f.severity.value,
            "severityScore": severity_score(f.severity),
            "confidence": f.confidence.value,
            "compositeConfidence": composite_confidence(f),
            "posterior": round(f.posterior, 4),
            "prior": round(f.prior, 4),
            "sprtDecision": f.sprt_decision.value,
            "source": f.source,
            "pocState": f.poc_state.value,
            "evidenceCount": len(f.evidence),
            "suggestedFix": f.suggested_fix or "",
            "pocPath": f.poc_path or "",
        },
    }


def to_sarif(scan: Scan, findings: List[Finding]) -> dict:
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "kwaro",
                    "informationUri": "https://github.com/vip-ultr/kwaro",
                    "version": "0.5.0",
                    "rules": [{"id": f.rule_id, "shortDescription": {"text": f.title},
                               "fullDescription": {"text": f.description or ""},
                               "properties": {"cwe": f.cwe, "severity": f.severity.value}}
                              for f in findings],
                }
            },
            "invocations": [{
                "executionSuccessful": True,
                "properties": {"scanId": scan.id, "profile": scan.profile,
                               "target": scan.target, "commit": scan.commit},
            }],
            "results": [_result(f) for f in findings],
        }],
    }


def to_json(scan: Scan, findings: List[Finding]) -> dict:
    return {
        "scan": scan.to_dict(),
        "findings": [{
            **f.to_dict(),
            "severityScore": severity_score(f.severity),
            "compositeConfidence": composite_confidence(f),
        } for f in findings],
        "summary": {
            "total": len(findings),
            "bySeverity": _count_by(findings, lambda f: f.severity.value),
            "kept": len([f for f in findings
                         if f.sprt_decision.value == "real" or f.posterior >= 0.5]),
        },
    }


def _count_by(items, key):
    out = {}
    for it in items:
        k = key(it)
        out[k] = out.get(k, 0) + 1
    return out


def write_report(scan: Scan, findings: List[Finding], fmt: str, path: str) -> None:
    if fmt == "sarif":
        with open(path, "w") as fh:
            json.dump(to_sarif(scan, findings), fh, indent=2)
    else:
        with open(path, "w") as fh:
            json.dump(to_json(scan, findings), fh, indent=2)
