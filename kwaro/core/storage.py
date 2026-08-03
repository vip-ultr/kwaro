"""kwaro core: SQLite storage (one file, zero-config, L8).

Persists Scan and Finding rows including the math fields from L7. No server, no
migrations framework. Schema is additive and versioned in code. Pure stdlib.
"""
from __future__ import annotations

import json
import os
import sqlite3
from typing import List, Optional

from .models import Finding, Scan, SprtDecision, Stage


DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".kwaro", "kwaro.db")


class Storage:
    def __init__(self, path: str = DEFAULT_DB) -> None:
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY, target TEXT, target_type TEXT,
                "commit" TEXT, provider TEXT, model TEXT, profile TEXT,
                status TEXT, started_at REAL, finished_at REAL,
                finding_count INTEGER, kept_count INTEGER, precision REAL, recall REAL
            )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY, scan_id TEXT, title TEXT, severity TEXT,
                cwe TEXT, rule_id TEXT, source TEXT, confidence TEXT,
                file TEXT, line_start INTEGER, line_end INTEGER, column INTEGER,
                snippet TEXT, description TEXT, suggested_fix TEXT, poc_path TEXT,
                poc_state TEXT, fingerprint TEXT, created_at REAL,
                prior REAL, posterior REAL, evidence TEXT, sprt_alpha REAL,
                sprt_beta REAL, sprt_decision TEXT, stage TEXT, loop_variant TEXT
            )"""
        )
        self.conn.commit()

    def save_scan(self, scan: Scan) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO scans
               (id, target, target_type, "commit", provider, model, profile,
                status, started_at, finished_at, finding_count, kept_count, precision, recall)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (scan.id, scan.target, scan.target_type, scan.commit, scan.provider,
             scan.model, scan.profile, scan.status, scan.started_at,
             scan.finished_at, scan.finding_count, scan.kept_count, scan.precision, scan.recall),
        )
        self.conn.commit()

    def save_finding(self, f: Finding) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO findings
               (id, scan_id, title, severity, cwe, rule_id, source, confidence,
                file, line_start, line_end, column, snippet, description,
                suggested_fix, poc_path, poc_state, fingerprint, created_at,
                prior, posterior, evidence, sprt_alpha, sprt_beta,
                sprt_decision, stage, loop_variant)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f.id, f.scan_id, f.title, f.severity.value, f.cwe, f.rule_id,
             f.source, f.confidence.value, f.file, f.line_start, f.line_end,
             f.column, f.snippet, f.description, f.suggested_fix, f.poc_path,
             f.poc_state.value, f.fingerprint, f.created_at, f.prior, f.posterior,
             json.dumps([vars(e) for e in f.evidence]), f.sprt_alpha, f.sprt_beta,
             f.sprt_decision.value, f.stage.value, json.dumps(f.loop_variant)),
        )
        self.conn.commit()

    def get_findings(self, scan_id: str) -> List[Finding]:
        rows = self.conn.execute(
            "SELECT * FROM findings WHERE scan_id = ?", (scan_id,)).fetchall()
        return [Finding.from_row(dict(r)) for r in rows]

    def close(self) -> None:
        self.conn.close()

    # --- L9 diff-aware rescan baseline ---
    def ensure_baseline_table(self) -> None:
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS baselines (
                target TEXT, profile TEXT, "commit" TEXT,
                hashes TEXT, scanned_at REAL,
                PRIMARY KEY (target, profile)
            )"""
        )
        self.conn.commit()

    def save_baseline(self, target: str, profile: str, commit: str,
                      hashes: dict, scanned_at: float) -> None:
        self.ensure_baseline_table()
        self.conn.execute(
            """INSERT OR REPLACE INTO baselines (target, profile, "commit", hashes, scanned_at)
               VALUES (?,?,?,?,?)""",
            (target, profile, commit, json.dumps(hashes), scanned_at),
        )
        self.conn.commit()

    def load_baseline(self, target: str, profile: str):
        self.ensure_baseline_table()
        row = self.conn.execute(
            'SELECT "commit", hashes FROM baselines WHERE target=? AND profile=?',
            (target, profile)).fetchone()
        if not row:
            return None
        return {"commit": row[0], "hashes": json.loads(row[1])}
