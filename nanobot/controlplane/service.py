"""Control-plane orchestration: events, projection, facade, safety."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from nanobot.controlplane.contracts import (
    ControlActionKind,
    ControlActionResult,
    ControlActionResponse,
    WsEnvelope,
)
from nanobot.controlplane.eventlog import ControlEventLog
from nanobot.controlplane.projection import ProjectionIndex
from nanobot.controlplane.runtime_facade import RuntimeFacade
from nanobot.controlplane.safety import SafetyGate


type WsBroadcaster = Callable[[str, dict[str, Any]], None]


class ControlPlaneService:
    """
    Orchestrates control-plane: normalizes events, maintains projection,
    executes control actions with safety gates, and broadcasts to WS.
    """

    def __init__(
        self,
        *,
        event_log: ControlEventLog | None = None,
        projection: ProjectionIndex | None = None,
        facade: RuntimeFacade | None = None,
        safety: SafetyGate | None = None,
        workspace: Path | None = None,
    ):
        self._event_log = event_log or ControlEventLog()
        self._workspace = workspace or Path.home() / ".nanobot" / "workspace"
        self._projection = projection or ProjectionIndex(self._event_log, self._workspace)
        self._facade = facade or RuntimeFacade()
        self._safety = safety or SafetyGate()
        self._ws_broadcast: WsBroadcaster | None = None

    def set_workspace(self, path: Path) -> None:
        self._workspace = path
        self._projection._workspace = path

    def set_facade(self, facade: RuntimeFacade) -> None:
        self._facade = facade

    def set_safety_token(self, token: str) -> None:
        self._safety._expected_token = token

    def set_ws_broadcast(self, fn: WsBroadcaster | None) -> None:
        self._ws_broadcast = fn

    def rebuild_projection(self) -> None:
        """Rebuild projection from canonical stores + event log."""
        self._projection.rebuild()

    def emit_event(
        self,
        event: str,
        data: dict[str, Any],
        *,
        event_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[str, int]:
        """Append event to log, apply to projection, and broadcast. Returns (event_id, seq)."""
        eid, seq = self._event_log.append(
            event, data, event_id=event_id, correlation_id=correlation_id
        )
        record = {
            "_type": "event",
            "eventId": eid,
            "eventSeq": seq,
            "event": event,
            "ts": datetime.now().isoformat(),
            "data": data,
            "correlationId": correlation_id,
        }
        self._projection.apply_live(record)
        if self._ws_broadcast:
            self._ws_broadcast(event, {"eventId": eid, "eventSeq": seq, **data})
        return eid, seq

    def emit_session_updated(
        self,
        session_id: str,
        *,
        channel: str = "",
        chat_id: str = "",
        status: str = "active",
        last_activity_at: datetime | None = None,
        turn_count: int = 0,
        latest_summary: str | None = None,
    ) -> tuple[str, int]:
        data = {
            "sessionId": session_id,
            "channel": channel or (session_id.split(":")[0] if ":" in session_id else "cli"),
            "chatId": chat_id or (session_id.split(":")[1] if ":" in session_id else session_id),
            "status": status,
            "lastActivityAt": (last_activity_at or datetime.now()).isoformat(),
            "turnCount": turn_count,
            "latestSummary": latest_summary,
        }
        return self.emit_event("session.updated", data)

    def emit_trajectory_step(
        self,
        session_id: str,
        step_type: str,
        *,
        actor: str = "assistant",
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> tuple[str, int]:
        data = {
            "sessionId": session_id,
            "type": step_type,
            "actor": actor,
            "payload": payload or {},
            "correlationId": correlation_id,
        }
        return self.emit_event(
            "trajectory.step", data, correlation_id=correlation_id
        )

    def emit_channel_health_changed(
        self,
        channel_id: str,
        state: str,
        *,
        reason: str | None = None,
        enabled: bool = True,
        error_count_1h: int = 0,
    ) -> tuple[str, int]:
        data = {
            "channelId": channel_id,
            "state": state,
            "reason": reason,
            "enabled": enabled,
            "errorCount1h": error_count_1h,
        }
        return self.emit_event("channel.health_changed", data)

    def emit_control_action_result(
        self,
        action_id: str,
        kind: str,
        result: str,
        *,
        error: str | None = None,
        state: str | None = None,
    ) -> tuple[str, int]:
        data = {
            "actionId": action_id,
            "kind": kind,
            "result": result,
            "error": error,
            "state": state,
            "ts": datetime.now().isoformat(),
        }
        return self.emit_event("control.action_result", data)

    # --- Read API (from projection + facade) ---

    def list_sessions(
        self,
        *,
        status: str | None = None,
        channel: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> tuple[list[Any], str | None]:
        from nanobot.controlplane.contracts import SessionStatus
        st = SessionStatus(status) if status else None  # type: ignore[arg-type]
        return self._projection.list_sessions(
            status=st, channel=channel, limit=limit, cursor=cursor
        )

    def get_session(self, session_id: str) -> Any | None:
        return self._projection.get_session(session_id) or self._facade.get_session(session_id)

    def get_trajectory_summary(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self._projection.get_trajectory_summary(session_id, limit=limit)

    def get_session_messages(self, session_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return last N messages for a session (for chat timeline)."""
        return self._facade.get_session_messages(session_id, limit=limit)

    def list_channels(self) -> list[Any]:
        channels = self._projection.list_channels()
        if not channels:
            return self._facade.get_channel_health()
        return channels

    def get_agent_status(self) -> Any | None:
        return self._projection.get_agent() or self._facade.get_agent_status()

    def get_stats_overview(self, window_hours: int = 1) -> dict[str, Any]:
        """Basic aggregated stats (placeholder for Week 2)."""
        sessions, _ = self.list_sessions(limit=1000)
        return {
            "sessions": len(sessions),
            "errors": 0,
            "latency": None,
            "throughput": None,
            "window": f"{window_hours}h",
        }

    def get_events_after(self, after_seq: int = 0, limit: int = 100) -> tuple[list[dict[str, Any]], int]:
        """Events after given seq for backfill; returns (records, last_seq). Deterministic ordering by eventSeq; replay is idempotent by eventId."""
        records = self._event_log.get_events_after(after_seq=after_seq, limit=limit)
        last = self._event_log.last_seq()
        return records, last

    # --- Control actions ---

    def execute_control_action(
        self,
        kind: ControlActionKind,
        target_id: str,
        *,
        idempotency_key: str,
        confirm_token: str | None = None,
        reason: str | None = None,
    ) -> ControlActionResponse:
        """Validate safety, dedupe by idempotency key, execute, audit, broadcast."""
        cached = self._safety.get_cached_result(idempotency_key)
        if cached:
            return ControlActionResponse(
                actionId=cached["actionId"],
                result=ControlActionResult(cached["result"]),
                state=cached.get("state"),
                error=cached.get("error"),
            )
        err = self._safety.validate_confirm(kind, confirm_token)
        if err:
            self._safety.cache_result(idempotency_key, ControlActionResult.REJECTED, error=err)
            self.emit_control_action_result(idempotency_key, kind.value, "rejected", error=err)
            return ControlActionResponse(
                actionId=idempotency_key,
                result=ControlActionResult.REJECTED,
                error=err,
            )
        # Audit: record control action request
        self._event_log.append(
            "control.action",
            {
                "actionId": idempotency_key,
                "kind": kind.value,
                "targetId": target_id,
                "requiresConfirm": self._safety.requires_confirm(kind),
                "requestedAt": datetime.now().isoformat(),
                "requestedBy": "operator",
                "reason": reason,
            },
        )
        # Execute
        if kind == ControlActionKind.CHANNEL_PAUSE:
            self._facade.set_channel_paused(target_id, True)
            state = "paused"
        elif kind == ControlActionKind.CHANNEL_RESUME:
            self._facade.set_channel_paused(target_id, False)
            state = "healthy"
        elif kind == ControlActionKind.GATEWAY_RESTART:
            state = "restart_requested"  # caller may handle actual restart
        else:
            state = None
        self._safety.cache_result(idempotency_key, ControlActionResult.COMPLETED, state=state)
        self.emit_control_action_result(idempotency_key, kind.value, "completed", state=state)
        return ControlActionResponse(
            actionId=idempotency_key,
            result=ControlActionResult.COMPLETED,
            state=state,
        )

    @property
    def event_log(self) -> ControlEventLog:
        return self._event_log

    @property
    def projection(self) -> ProjectionIndex:
        return self._projection

    @property
    def facade(self) -> RuntimeFacade:
        return self._facade

    @property
    def safety(self) -> SafetyGate:
        return self._safety
