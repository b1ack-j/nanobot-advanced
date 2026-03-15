"""Query-optimized read model (projection) over canonical stores + event log."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from nanobot.controlplane.contracts import (
    AgentRuntimeView,
    ChannelHealthView,
    ChannelState,
    SessionStatus,
    SessionView,
)
from nanobot.controlplane.eventlog import ControlEventLog


class ProjectionIndex:
    """
    In-memory index for dashboard read paths.
    Rebuildable from canonical session files + control event log.
    Apply events idempotently by eventId to avoid duplicate updates.
    """

    def __init__(self, event_log: ControlEventLog, workspace: Path):
        self._event_log = event_log
        self._workspace = workspace
        self._sessions: dict[str, SessionView] = {}
        self._channels: dict[str, ChannelHealthView] = {}
        self._agent: AgentRuntimeView | None = None
        self._trajectory_by_session: dict[str, list[dict[str, Any]]] = {}
        self._applied_event_ids: set[str] = set()
        self._last_applied_seq = 0

    def rebuild(self) -> None:
        """Load from canonical session files and replay event log with idempotent apply."""
        self._sessions.clear()
        self._trajectory_by_session.clear()
        self._applied_event_ids.clear()
        self._last_applied_seq = 0

        # Bootstrap sessions from workspace session files
        sessions_dir = self._workspace / "sessions"
        if sessions_dir.exists():
            for p in sessions_dir.glob("*.jsonl"):
                try:
                    key = p.stem.replace("_", ":", 1) if "_" in p.stem else p.stem
                    with open(p, encoding="utf-8") as f:
                        msg_count = 0
                        for line in f:
                            if line.strip() and not line.strip().startswith("{"):
                                continue
                            if '"_type"' in line and "metadata" in line:
                                continue
                            try:
                                _ = line.strip()
                                if _:
                                    msg_count += 1
                            except Exception:
                                pass
                    # Simple turn count from line count (user/assistant/tool messages)
                    turn_count = max(0, msg_count // 2)
                    self._sessions[key] = SessionView(
                        id=key,
                        channel=key.split(":")[0] if ":" in key else "cli",
                        chatId=key.split(":")[1] if ":" in key else key,
                        status=SessionStatus.ACTIVE,
                        lastActivityAt=datetime.now(),
                        turnCount=turn_count,
                    )
                except Exception:
                    pass

        # Replay events (idempotent by eventId)
        for record in self._event_log.load_replay_sync(dedupe_by_id=True):
            self._apply_event(record)
            self._last_applied_seq = max(
                self._last_applied_seq, record.get("eventSeq", 0)
            )

    def _apply_event(self, record: dict[str, Any]) -> None:
        """Apply a single event to projection (idempotent by eventId)."""
        eid = record.get("eventId", "")
        if eid and eid in self._applied_event_ids:
            return
        if eid:
            self._applied_event_ids.add(eid)

        event = record.get("event", "")
        data = record.get("data", {})
        ts_str = record.get("ts", "")
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")) if ts_str else datetime.now()

        if event == "session.updated":
            sid = data.get("sessionId", "")
            if sid:
                self._sessions[sid] = SessionView(
                    id=sid,
                    channel=data.get("channel", sid.split(":")[0] if ":" in sid else "cli"),
                    chatId=data.get("chatId", sid.split(":")[1] if ":" in sid else sid),
                    status=SessionStatus(data.get("status", "active")),
                    lastActivityAt=datetime.fromisoformat(data["lastActivityAt"].replace("Z", "+00:00"))
                    if isinstance(data.get("lastActivityAt"), str)
                    else ts,
                    turnCount=data.get("turnCount", 0),
                    latestSummary=data.get("latestSummary"),
                )
        elif event == "channel.health_changed":
            cid = data.get("channelId", "")
            if cid:
                self._channels[cid] = ChannelHealthView(
                    channelId=cid,
                    enabled=data.get("enabled", True),
                    state=ChannelState(data.get("state", "healthy")),
                    lastHeartbeatAt=ts if data.get("lastHeartbeatAt") else None,
                    errorCount1h=data.get("errorCount1h", 0),
                    note=data.get("note"),
                )
        elif event == "trajectory.step":
            sid = data.get("sessionId", "")
            if sid:
                if sid not in self._trajectory_by_session:
                    self._trajectory_by_session[sid] = []
                self._trajectory_by_session[sid].append(
                    {
                        "eventId": eid or data.get("eventId"),
                        "ts": ts_str,
                        "sessionId": sid,
                        "type": data.get("type", "turn.started"),
                        "actor": data.get("actor", "assistant"),
                        "payload": data.get("payload", {}),
                        "correlationId": data.get("correlationId"),
                        "eventSeq": record.get("eventSeq", 0),
                    }
                )
                # Keep last N per session to bound memory
                if len(self._trajectory_by_session[sid]) > 500:
                    self._trajectory_by_session[sid] = self._trajectory_by_session[sid][-400:]

    def apply_live(self, record: dict[str, Any]) -> None:
        """Apply one event from live stream (same idempotency)."""
        self._apply_event(record)

    def list_sessions(
        self,
        *,
        status: SessionStatus | None = None,
        channel: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> tuple[list[SessionView], str | None]:
        """List sessions with optional filters. Returns (items, next_cursor)."""
        items = list(self._sessions.values())
        if status is not None:
            items = [s for s in items if s.status == status]
        if channel is not None:
            items = [s for s in items if s.channel == channel]
        items.sort(key=lambda s: s.last_activity_at, reverse=True)
        start = 0
        if cursor:
            for i, s in enumerate(items):
                if s.id == cursor:
                    start = i + 1
                    break
        page = items[start : start + limit]
        next_cursor = items[start + limit].id if start + limit < len(items) else None
        return page, next_cursor

    def get_session(self, session_id: str) -> SessionView | None:
        return self._sessions.get(session_id)

    def get_trajectory_summary(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Recent trajectory steps for a session (for timeline)."""
        steps = self._trajectory_by_session.get(session_id, [])
        return steps[-limit:]

    def list_channels(self) -> list[ChannelHealthView]:
        return list(self._channels.values())

    def get_channel(self, channel_id: str) -> ChannelHealthView | None:
        return self._channels.get(channel_id)

    def get_agent(self) -> AgentRuntimeView | None:
        return self._agent

    def set_agent(self, view: AgentRuntimeView) -> None:
        self._agent = view

    def last_applied_seq(self) -> int:
        return self._last_applied_seq
