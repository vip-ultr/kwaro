"""kwaro web: FastAPI app + WebSocket (the `serve` extra, L11).

Serves the hand-written static bundle and exposes:
  GET  /                 -> index.html
  GET  /static/<file>    -> bundle assets
  POST /api/scan         -> run a scan, return findings (or an export path)
  POST /api/chat         -> one chat turn (model if configured, else static note)
  WS   /ws/activity      -> live scan activity stream (optional)

FastAPI/uvicorn/websockets are ONLY imported when `kwaro serve` runs, so the CLI
stays zero-dependency (L1). If the extra isn't installed, `kwaro serve` prints a
clear install hint instead of crashing.

NOTE: no `from __future__ import annotations` here on purpose. It stringifies
annotations, which breaks FastAPI's Pydantic-model body detection for nested
models. Models are defined at module level so FastAPI can resolve them.
"""
import os

import pydantic

from .core.models import Finding
from .core.rank import composite_confidence
from . import __main__ as cli

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web", "static")


class ScanReq(pydantic.BaseModel):
    target: str = ""
    profile: str = "generic"
    pocs: bool = False
    rescan: bool = False
    format: "str" = None


class ChatReq(pydantic.BaseModel):
    target: str = ""
    message: str = ""


def create_app():
    """Build and return the FastAPI app (imports the heavy deps here)."""
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles

    app = FastAPI(title="kwaro", version="0.6.0")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    def _finding_dict(f: Finding) -> dict:
        d = f.to_dict()
        d["compositeConfidence"] = composite_confidence(f)
        return d

    @app.post("/api/scan")
    async def api_scan(req: ScanReq):
        if not req.target:
            return {"error": "missing target"}
        cli.cmd_scan(req.target, req.profile, req.pocs, None, req.rescan, req.format)
        if req.format:
            path = f"kwaro-report.{'sarif' if req.format == 'sarif' else 'json'}"
            return {"export_path": path, "report": True}
        from .core.storage import Storage
        store = Storage()
        row = store.conn.execute(
            "SELECT id FROM scans ORDER BY rowid DESC LIMIT 1").fetchone()
        findings = store.get_findings(row[0]) if row else []
        store.close()
        return {"report": True, "findings": [_finding_dict(f) for f in findings]}

    @app.post("/api/chat")
    async def api_chat(req: ChatReq):
        if not req.message:
            return {"reply": "(empty message)"}
        try:
            from .core.config import Config
            from .core.providers import from_config
            from .core.workspace import Workspace
            from .chat.agent import ChatAgent
            from .core.providers.base import ToolSpec

            cfg = Config.load()
            ws = Workspace.from_target(req.target or ".")
            provider = from_config(cfg)
            agent = ChatAgent(provider, ws.root)

            def read_file(a):
                p = os.path.join(ws.root, a.get("path", ""))
                return open(p, errors="ignore").read()[:4000] if os.path.isfile(p) else "no file"
            def run_analyzer(a):
                found = cli.analyze_file(os.path.join(ws.root, a.get("path", ""))) if a.get("path") else []
                return "\n".join(f"{f.severity.value}: {f.title}" for f in found) or "no findings"
            def done(a): return "DONE: " + a.get("summary", "")
            agent.register(ToolSpec(name="read_file", description="read a file",
                                    parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}), read_file)
            agent.register(ToolSpec(name="run_analyzer", description="run analyzers",
                                    parameters={"type": "object", "properties": {"path": {"type": "string"}}}), run_analyzer)
            agent.register(ToolSpec(name="done", description="finish",
                                    parameters={"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}), done)
            return {"reply": agent.run(req.message)}
        except Exception as e:
            return {"reply": f"(chat needs a configured model; static-only note) {e}"}

    @app.websocket("/ws/activity")
    async def ws_activity(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                await ws.receive_text()
                await ws.send_json({"event": "ping"})
        except Exception:
            pass

    return app


def run(port: int = 8080, host: str = "127.0.0.1") -> None:
    try:
        import uvicorn  # noqa
    except ImportError:
        print("kwaro serve needs the 'serve' extra:  uv pip install 'kwaro[serve]'  "
              "(or pip install fastapi uvicorn websockets)")
        return
    app = create_app()
    print(f"kwaro: serving UI at http://{host}:{port}  (Ctrl-C to stop)")
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="warning")
