"""Phase 6 tests: the `serve` web UI (requires the optional 'serve' extra).

These tests are skipped automatically if fastapi/httpx aren't installed, so the
core CLI test suite stays zero-dependency. When the extra is present, they boot
the app with TestClient and hit the real endpoints (which run the actual scan
pipeline), proving the UI wiring end to end.
"""
import os

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("httpx")  # TestClient needs httpx


@pytest.fixture(scope="module")
def client():
    from kwaro.serve import create_app
    from fastapi.testclient import TestClient
    return TestClient(create_app())


def test_index_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "kwaro" in r.text
    assert "findings" in r.text.lower()


def test_static_assets(client):
    r = client.get("/static/app.js")
    assert r.status_code == 200
    assert "use strict" in r.text


def test_api_scan_runs_pipeline(client, tmp_path):
    # point at the in-repo fixture so we exercise the real analyzers
    target = os.path.join(os.path.dirname(__file__), "fixtures", "vuln-repo")
    r = client.post("/api/scan", json={"target": target, "profile": "generic"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("report") is True
    # the fixture yields several findings across rules
    assert len(data["findings"]) >= 3
    # math fields carried into the UI payload
    f0 = data["findings"][0]
    assert "posterior" in f0
    assert "compositeConfidence" in f0
    assert "sprt_decision" in f0


def test_api_scan_sarif_export(client, tmp_path):
    target = os.path.join(os.path.dirname(__file__), "fixtures", "vuln-repo")
    r = client.post("/api/scan", json={"target": target, "format": "sarif"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("export_path", "").endswith(".sarif")
    # clean up the exported file
    p = data["export_path"]
    if os.path.exists(p):
        os.remove(p)


def test_api_chat_returns_reply(client):
    r = client.post("/api/chat", json={"target": ".", "message": "any"})
    assert r.status_code == 200
    assert "reply" in r.json()
