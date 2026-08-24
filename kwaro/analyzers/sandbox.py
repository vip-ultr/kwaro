"""Sandbox-gated PoC executor (Phase C, locked decision L6).

Takes a GENERATED PoC file and runs it in a constrained sandbox:

- isolated temp working directory (deleted after)
- NO network: sockets are blocked at the Python layer before exec
- wall-clock timeout (default 10s) -> kill on expiry
- output capped; exit code + stderr captured
- the PoC must signal success itself: exit 0 AND print a line starting with
  KWaro_POC_CONFIRMED. Anything else classifies UNVERIFIED.

Honest limits: this is process-level sandboxing (resource/time/no-network),
NOT a VM or container. L6 says run untrusted PoCs only in a container/VM;
this executor adds defense-in-depth for the local default path but does not
replace that advice.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from ..core.models import Finding, PocState

CONFIRM_MARKER = "KWaro_POC_CONFIRMED"
DEFAULT_TIMEOUT_S = 10
MAX_OUTPUT = 8192

# Preloaded into the child so `import socket` fails fast inside the PoC.
_NO_NET_PREIMPORT = (
    "import socket as _s\n"
    "class _NoNet(Exception):\n    pass\n"
    "def _blocked(*a, **k):\n    raise _NoNet('kwaro sandbox: network disabled')\n"
    "_s.socket = _blocked\n"
    "_s.create_connection = _blocked\n"
    "try:\n    import socketserver as _ss\n    _ss.TCPServer = None\n"
    "except Exception:\n    pass\n"
)


def execute_poc(f: Finding, timeout_s: int = DEFAULT_TIMEOUT_S,
                keep_dir: bool = False) -> dict:
    """Run f.poc_path in the sandbox and set f.poc_state accordingly.

    Returns an evidence dict {state, exit_code, stdout, stderr, duration_hint}.
    VERIFIED requires: process ran, exited 0, and printed CONFIRM_MARKER.
    Every other outcome is UNVERIFIED (never raises severity, per L6).
    """
    if not getattr(f, "poc_path", None) or not os.path.exists(f.poc_path):
        return {"state": PocState.NONE.value}

    tmpdir = tempfile.mkdtemp(prefix="kwaro-poc-")
    workdir = os.path.join(tmpdir, "ws")
    os.makedirs(workdir)
    shutil.copy(f.poc_path, workdir)
    poc_file = os.path.basename(f.poc_path)

    cmd = [sys.executable, "-c",
           _NO_NET_PREIMPORT + "exec(open(%r).read())" % poc_file]
    result = {"state": PocState.UNVERIFIED.value, "exit_code": None,
              "stderr": "sandbox did not run"}
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, timeout=timeout_s,
            capture_output=True, text=True, errors="replace",
            env={"PATH": os.environ.get("PATH", ""), "HOME": workdir,
                 "PYTHONHASHSEED": "0"},
        )
        out = (proc.stdout or "")[:MAX_OUTPUT]
        err = (proc.stderr or "")[:MAX_OUTPUT]
        verified = proc.returncode == 0 and CONFIRM_MARKER in out
        state = PocState.VERIFIED if verified else PocState.UNVERIFIED
        result = {
            "state": state.value,
            "exit_code": proc.returncode,
            "stdout": out,
            "stderr": err[:2000],
        }
    except subprocess.TimeoutExpired:
        result = {"state": PocState.UNVERIFIED.value,
                  "exit_code": None, "stderr": "timeout after %ss" % timeout_s}
    finally:
        if keep_dir:
            result["workdir"] = workdir  # only when explicitly asked
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)

    f.poc_state = PocState(result["state"])
    return result
