"""Observability correctness: event log ordering and projection replay idempotency."""

from pathlib import Path

from nanobot.controlplane.eventlog import ControlEventLog
from nanobot.controlplane.observability import (
    check_event_log_ordering,
    check_projection_rebuild_idempotent,
)


def test_event_log_ordering_empty(tmp_path: Path) -> None:
    ok, msg = check_event_log_ordering(tmp_path)
    assert ok is True
    assert "No event log" in msg or "OK" in msg


def test_event_log_ordering_monotonic(tmp_path: Path) -> None:
    log = ControlEventLog(tmp_path)
    log.append("session.updated", {"sessionId": "a:1"})
    log.append("session.updated", {"sessionId": "b:2"})
    ok, msg = check_event_log_ordering(tmp_path)
    assert ok is True, msg
    assert "OK" in msg


def test_projection_rebuild_idempotent(tmp_path: Path) -> None:
    log = ControlEventLog(tmp_path)
    log.append("session.updated", {"sessionId": "c:3", "channel": "c", "chatId": "3", "status": "active", "lastActivityAt": "2026-01-01T00:00:00", "turnCount": 0})
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "sessions").mkdir()
    ok, msg = check_projection_rebuild_idempotent(log, workspace)
    assert ok is True, msg
