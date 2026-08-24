"""Phase C eval (L13): sandbox-gated PoC executor (L6).

The executor must classify correctly across the five outcome classes and MUST
block network access inside the child. Runs only local python subprocesses;
no network needed by the tests themselves.
"""
import os
import tempfile

import pytest

from kwaro.analyzers.sandbox import CONFIRM_MARKER, execute_poc
from kwaro.core.models import Finding, PocState


def make_finding(body: str) -> Finding:
    f = Finding(title="t", rule_id="x.y", file="a.py", line_start=1)
    d = tempfile.mkdtemp()
    f.poc_path = os.path.join(d, "poc.py")
    with open(f.poc_path, "w") as fh:
        fh.write(body)
    return f


def test_confirming_poc_is_verified():
    f = make_finding('print("%s: reproduced")\n' % CONFIRM_MARKER)
    r = execute_poc(f)
    assert r["state"] == PocState.VERIFIED.value
    assert f.poc_state == PocState.VERIFIED


def test_crashing_poc_is_unverified():
    f = make_finding("raise RuntimeError('boom')\n")
    r = execute_poc(f)
    assert r["state"] == PocState.UNVERIFIED.value


def test_network_is_blocked():
    # socket.socket is replaced before exec; PoC cannot open one
    f = make_finding(
        "import socket\n"
        "s = socket.socket()\n"  # must raise -> no marker printed
        "print('%s')\n" % CONFIRM_MARKER
    )
    r = execute_poc(f)
    assert r["state"] == PocState.UNVERIFIED.value


def test_silent_success_without_marker_is_unverified():
    f = make_finding("pass\n")
    assert execute_poc(f)["state"] == PocState.UNVERIFIED.value


def test_timeout_is_unverified():
    f = make_finding("while True:\n    pass\n")
    r = execute_poc(f, timeout_s=2)
    assert r["state"] == PocState.UNVERIFIED.value
    assert "timeout" in (r.get("stderr") or "")


def test_missing_poc_is_none():
    f = Finding(title="t", rule_id="x.y", file="a.py", line_start=1)
    assert execute_poc(f)["state"] == PocState.NONE.value


def test_workdir_removed_after_run():
    f = make_finding("pass\n")
    r = execute_poc(f)
    assert "workdir" not in r  # temp evidence dir cleaned by default
