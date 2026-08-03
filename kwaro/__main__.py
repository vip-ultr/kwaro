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
import sys
from typing import Optional

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


# --- static analyzers (Phase 3): deterministic rule sets from kwaro/analyzers ---
# The math spine (prove/fix/verify) still runs over whatever findings these yield.

def analyze_file(path: str, only: Optional[list] = None) -> list[Finding]:
    from .analyzers import scan_file as a_scan

    out: list[Finding] = []
    try:
        with open(path, "r", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return out
    return a_scan(path, lines, only)


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


def cmd_scan(target: str, profile: str = "generic", generate_pocs: bool = False,
             provider_for_poc=None) -> int:
    from .analyzers import enabled_names
    from .core.profiles import Profile
    from .core.rank import composite_confidence

    prof = Profile.load(profile)
    only = enabled_names(prof.enable) if prof.enable else None
    print(f"kwaro: scanning {target} (profile: {profile}, {len(only) if only else 'all'} analyzers, math spine on)")
    ws = Workspace.from_target(target)
    findings: list[Finding] = []
    for p in ws.file_hashes:
        if p.endswith((".py", ".js", ".ts", ".go", ".java", ".php", ".sol", ".rs", ".html", ".jsx", ".vue", ".hbs", ".ejs")):
            findings.extend(analyze_file(p, only))

    scan = Scan(target=target, target_type=ws.target_type, commit=ws.commit,
                provider="static", model="none", profile=profile)
    store = Storage()
    store.save_scan(scan)

    # Pipeline: PROVE/FIX/VERIFY (math spine) -> aggregate -> de-dupe (L4) -> rank (L3)
    from .core.pipeline import run_pipeline, attach_scan_math
    result = run_pipeline(
        findings, prove, fix, verify_finding, cap=12,
        generate_pocs=generate_pocs, provider=provider_for_poc,
    )
    for f in result["ranked"]:
        f.scan_id = scan.id
        store.save_finding(f)

    attach_scan_math(scan, result)
    scan.status = "done"
    store.save_scan(scan)
    store.close()

    # --- math-aware report ---
    kept = result["kept"]
    print(f"\n{len(result['unique'])} unique findings (from {len(findings)} raw), "
          f"{len(kept)} kept after prove/verify\n")
    for f in kept:
        conf = composite_confidence(f)
        print(f"  {f.severity.value.upper():8} {f.file}:{f.line_start:<4} {f.title}")
        print(f"           conf={conf:.3f} prior={f.prior:.3f} posterior={f.posterior:.3f} "
              f"sprt={f.sprt_decision.value} poc={f.poc_state.value}")
    print(f"\nloop variant trace: {' -> '.join(str(x) for x in result['trace'])}")
    print(f"pipeline graph valid: {result['graph_valid']} ({result['graph_why']})")
    print(f"de-duplicated: {len(findings)} raw -> {len(result['unique'])} unique")
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
        profile = "generic"
        generate_pocs = False
        rest = args[1:]
        if "--profile" in rest:
            idx = rest.index("--profile")
            if idx + 1 < len(rest):
                profile = rest[idx + 1]
                rest = rest[:idx] + rest[idx + 2:]
        if "--pocs" in rest:
            generate_pocs = True
            rest = [a for a in rest if a != "--pocs"]
        return cmd_scan(rest[0], profile, generate_pocs)
    if cmd == "chat":
        if len(args) < 2:
            print("kwaro chat: missing <path|url>")
            return 2
        return cmd_chat(args[1])
    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
