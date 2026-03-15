"""Control plane API: REST contracts and core flows."""

from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from nanobot.controlplane.api.app import create_control_app, _redact_secrets
from nanobot.controlplane.service import ControlPlaneService
from nanobot.controlplane.runtime_facade import RuntimeFacade


def test_health_endpoints() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc)
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_config_redaction() -> None:
    out = _redact_secrets({"providers": {"openrouter": {"apiKey": "sk-secret"}}, "x": "y"})
    assert out["providers"]["openrouter"]["apiKey"] == "***"
    assert out["x"] == "y"


def test_config_endpoint_returns_structure() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc, config_snapshot={"gateway": {"port": 18790}})
    client = TestClient(app)
    r = client.get("/api/control/config")
    assert r.status_code == 200
    data = r.json()
    assert "gateway" in data
    assert data["gateway"]["port"] == 18790


def test_sessions_list_empty() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc)
    client = TestClient(app)
    r = client.get("/api/control/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "nextCursor" in data


def test_chat_send_requires_session_and_content() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc)
    client = TestClient(app)
    r = client.post("/api/control/chat/send", json={})
    assert r.status_code == 400
    r = client.post("/api/control/chat/send", json={"sessionId": "cli:direct"})
    assert r.status_code == 400
    r = client.post("/api/control/chat/send", json={"content": "hi"})
    assert r.status_code == 400


def test_chat_send_503_when_no_submit_fn() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc)
    client = TestClient(app)
    r = client.post("/api/control/chat/send", json={"sessionId": "cli:direct", "content": "hello"})
    assert r.status_code == 503


def test_events_backfill_endpoint() -> None:
    svc = ControlPlaneService(workspace=Path("/tmp/test"))
    app = create_control_app(svc)
    client = TestClient(app)
    r = client.get("/api/control/events?after_seq=0&limit=10")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "lastSeq" in data
