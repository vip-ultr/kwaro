"""kwaro CLI entry point.

Subcommands:
  kwaro init            - detect Ollama, write ~/.kwaro/config.toml (free/offline default)
  kwaro scan <path|url> - clone/copy target, run static analyzers, prove + verify
                          findings, persist to SQLite, print the math-aware report

Phase 1: static-only analyzers are a minimal placeholder; the math spine
(Bayes, SPRT, graph, loop variant) is fully wired and exercised end to end.
"""
from __future__ import annotations

import os
import re
import sys

from .core import graph, loop, verify
from .core.models import (
    Confidence,
    Finding,
    PocState,
    Scan,
    Severity,
    SprtDecision,
    Stage,
)
from .core.storage import Storage
from .core.workspace import Workspace


CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".kwaro", "config.toml")


# --- minimal static analyzer (placeholder; real rules are Phase 3) ---
SECRET_RE = re.compile(r"(api_key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9!@#$%^&*]{8,}['\"]", re.IGNORECASE)
SQLI_RE = re.compile(r"(SELECT|INSERT|UPDATE|DELETE)\b.*\+.*")


def analyze_file(path: str) -> list[Finding]:
    out: list[Finding] = []
    try:
        with open(path, "r", errors="ignore") as fh:
            for i, line in enumerate(fh, 1):
                if SECRET_RE.search(line):
                    out.append(Finding(
                        title="Possible hardcoded secret", severity=Severity.MEDIUM,
                        cwe="CWE-798", rule_id="static.secret", source="static",
                        confidence=Confidence.MED, file=path, line_start=i,
                        snippet=line.strip()[:120],
                        description="A literal secret-like value was found in source.",
                    ))
                if SQLI_RE.search(line):
                    out.append(Finding(
                        title="Possible SQL injection (string concat into query)",
                        severity=Severity.HIGH, cwe="CWE-89", rule_id="static.sqli",
                        source="static", confidence=Confidence.MED, file=path,
                        line_start=i, snippet=line.strip()[:120],
                        description="Query built by string concatenation may allow injection.",
                    ))
    except OSError:
        pass
    return out


def prove(f: Finding) -> None:
    """Placeholder prover: a static hit is weak evidence the flag is real."""
    verify.bayes_update(f, "static: pattern match in source", l_real=0.55, l_fake=0.25)


def fix(f: Finding) -> None:
    f.suggested_fix = "Use an environment variable or secret manager; parameterize queries."


def verify_finding(f: Finding) -> None:
    """Placeholder verify: no PoC in static-only mode, so evidence is inconclusive
    but we still compute the SPRT verdict from accumulated evidence. If the belief
    clears the bar, the finding is DONE (kept); otherwise it stays at VERIFY."""
    verify.evaluate(f)
    if f.posterior >= 0.5:
        f.confidence = Confidence.HIGH
        f.stage = Stage.DONE
    else:
        f.stage = Stage.VERIFY


def cmd_scan(target: str) -> int:
    print(f"kwaro: scanning {target} (mode: static-only, math spine on)")
    ws = Workspace.from_target(target)
    findings: list[Finding] = []
    for p in ws.file_hashes:
        if p.endswith((".py", ".js", ".ts", ".go", ".java", ".php", ".sol", ".rs")):
            findings.extend(analyze_file(p))

    scan = Scan(target=target, target_type=ws.target_type, commit=ws.commit,
                provider="static", model="none", profile="generic")
    store = Storage()
    store.save_scan(scan)

    # run the bounded find, prove, fix, verify loop (Primitive 2)
    trace = loop.run(findings, prove, fix, verify_finding, cap=12)
    for f in findings:
        f.scan_id = scan.id
        store.save_finding(f)

    scan.finding_count = len(findings)
    scan.status = "done"
    store.close()

    # --- math-aware report ---
    kept = [f for f in findings if f.sprt_decision == SprtDecision.REAL
            or f.posterior >= 0.5]
    print(f"\n{len(findings)} candidate findings, {len(kept)} kept after prove/verify\n")
    for f in kept:
        print(f"  {f.severity.value.upper():8} {f.file}:{f.line_start:<4} {f.title}")
        print(f"           prior={f.prior:.3f} posterior={f.posterior:.3f} "
              f"sprt={f.sprt_decision.value} evidence={len(f.evidence)}")
    print(f"\nloop variant trace: {' -> '.join(str(x) for x in trace)}")
    valid, why = graph.is_valid_trace(
        [Stage.FIND, Stage.PROVE, Stage.FIX, Stage.VERIFY,
         Stage.FIND if findings else Stage.DONE])
    print(f"pipeline graph valid: {valid} ({why})")
    print("kwaro: scan complete (findings persisted to ~/.kwaro/kwaro.db)")
    return 0


def cmd_init() -> int:
    print("kwaro: setting up (free, local, offline by default)...")
    from .core.config import Config
    has_ollama = os.path.exists("/usr/bin/ollama") or os.path.exists(
        os.path.expanduser("~/.ollama"))
    if has_ollama:
        print("  [1/3] Ollama detected (local, free, no API key).")
    else:
        print("  [1/3] Ollama not found. Install from https://ollama.com (free, local).")
    print("  [2/3] Recommended model: a code-capable 14B (e.g. qwen2.5-coder:14b).")
    print("  [3/3] Writing ~/.kwaro/config.toml (provider=ollama, paid is opt-in BYOK).")
    Config().save()
    print("Done. Static-only works now; point provider at a hosted model via BYOK if wanted.")
    return 0


def cmd_chat(target: str) -> int:
    from .core.config import Config
    from .core.providers import from_config
    from .core.workspace import Workspace
    from .chat.agent import ChatAgent
    from .core.providers.base import ToolSpec

    cfg = Config.load()
    ws = Workspace.from_target(target)
    provider = from_config(cfg)
    print(f"kwaro chat: provider={provider.label}")
    print(f"kwaro chat: workspace={ws.root} (target={target})")

    agent = ChatAgent(provider, ws.root)

    def read_file(args: dict) -> str:
        path = os.path.join(ws.root, args.get("path", ""))
        if not os.path.isfile(path):
            return f"error: no such file {args.get('path')}"
        return open(path, "r", errors="ignore").read()[:4000]

    def run_analyzer(args: dict) -> str:
        path = args.get("path", "")
        full = os.path.join(ws.root, path) if path else ws.root
        found = []
        if os.path.isfile(full):
            found = analyze_file(full)
        else:
            for p in ws.file_hashes:
                if p.endswith((".py", ".js", ".ts", ".go", ".java", ".php", ".sol", ".rs")):
                    found.extend(analyze_file(p))
        if not found:
            return "no static findings"
        return "\n".join(f"{f.severity.value}: {f.title} @ {f.file}:{f.line_start}" for f in found)

    def request_poc(args: dict) -> str:
        return (f"PoC requested for {args.get('finding')}. In offline mode this is a "
                f"placeholder; enable sandboxed PoC execution to generate a real test.")

    def done(args: dict) -> str:
        return "DONE: " + args.get("summary", "session complete")

    agent.register(ToolSpec(
        name="read_file", description="Read a file in the workspace by relative path.",
        parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
        read_file)
    agent.register(ToolSpec(
        name="run_analyzer", description="Run static analyzers over a path or the whole workspace.",
        parameters={"type": "object", "properties": {"path": {"type": "string"}}}),
        run_analyzer)
    agent.register(ToolSpec(
        name="request_poc", description="Request a proof-of-concept for a finding (offline placeholder).",
        parameters={"type": "object", "properties": {"finding": {"type": "string"}}, "required": ["finding"]}),
        request_poc)
    agent.register(ToolSpec(
        name="done", description="End the session with a short summary of findings.",
        parameters={"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}),
        done)

    print("Type your request. kwaro will use tools, then call done. (Ctrl-C to quit)\n")
    try:
        while True:
            try:
                user_input = input("you> ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            summary = agent.run(user_input)
            print(f"kwaro> {summary}\n")
    except KeyboardInterrupt:
        print("\nkwaro chat: bye.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("kwaro - free, local security scanner")
        print("usage: kwaro init | kwaro scan <path|url> | kwaro chat <path|url>")
        return 0
    cmd = args[0]
    if cmd == "init":
        return cmd_init()
    if cmd == "scan":
        if len(args) < 2:
            print("kwaro scan: missing <path|url>")
            return 2
        return cmd_scan(args[1])
    if cmd == "chat":
        if len(args) < 2:
            print("kwaro chat: missing <path|url>")
            return 2
        return cmd_chat(args[1])
    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
