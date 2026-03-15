"""Stable control/query abstraction over existing runtime components (no protocol rewrites)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nanobot.controlplane.contracts import (
    AgentRuntimeView,
    AgentState,
    ChannelHealthView,
    ChannelState,
    SessionStatus,
    SessionView,
)

if TYPE_CHECKING:
    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.channels.manager import ChannelManager
    from nanobot.session.manager import SessionManager


class RuntimeFacade:
    """
    Read and control abstraction over AgentLoop, ChannelManager, SessionManager.
    Does not rewrite channel protocols; exposes query and optional control state.
    """

    def __init__(
        self,
        *,
        session_manager: SessionManager | None = None,
        channel_manager: ChannelManager | None = None,
        agent_loop: AgentLoop | None = None,
        bus: MessageBus | None = None,
    ):
        self._session_manager = session_manager
        self._channel_manager = channel_manager
        self._agent_loop = agent_loop
        self._bus = bus
        self._paused_channel_ids: set[str] = set()

    def get_sessions(self) -> list[SessionView]:
        """Build session list from SessionManager (canonical source)."""
        if not self._session_manager:
            return []
        out = []
        for item in self._session_manager.list_sessions():
            key = item.get("key", "")
            if not key:
                continue
            updated = item.get("updated_at", "")
            try:
                last_at = datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else datetime.now()
            except Exception:
                last_at = datetime.now()
            channel = key.split(":")[0] if ":" in key else "cli"
            chat_id = key.split(":")[1] if ":" in key else key
            status = SessionStatus.PAUSED if key in self._paused_channel_ids else SessionStatus.ACTIVE
            # turn_count from session file would require reading; use 0 as placeholder
            out.append(
                SessionView(
                    id=key,
                    channel=channel,
                    chatId=chat_id,
                    status=status,
                    lastActivityAt=last_at,
                    turnCount=0,
                )
            )
        return out

    def get_session(self, session_id: str) -> SessionView | None:
        """Get one session by id (channel:chat_id)."""
        for s in self.get_sessions():
            if s.id == session_id:
                return s
        return None

    def get_channel_health(self) -> list[ChannelHealthView]:
        """Build channel health list from ChannelManager."""
        if not self._channel_manager:
            return []
        out = []
        status = self._channel_manager.get_status()
        for name, info in status.items():
            running = info.get("running", False)
            paused = name in self._paused_channel_ids
            if paused:
                state = ChannelState.PAUSED
            elif running:
                state = ChannelState.HEALTHY
            else:
                state = ChannelState.DOWN
            out.append(
                ChannelHealthView(
                    channelId=name,
                    enabled=True,
                    state=state,
                    lastHeartbeatAt=datetime.now() if running else None,
                    errorCount1h=0,
                    note="",
                )
            )
        return out

    def get_agent_status(self) -> AgentRuntimeView | None:
        """Build agent runtime view from AgentLoop and bus."""
        if not self._agent_loop:
            return None
        running = getattr(self._agent_loop, "_running", False)
        active_tasks = getattr(self._agent_loop, "_active_tasks", {})
        active_count = sum(1 for tasks in active_tasks.values() if tasks)
        queue_depth = self._bus.inbound_size if self._bus else 0
        state = AgentState.BUSY if active_count > 0 else (AgentState.RUNNING if running else AgentState.STOPPED)
        model = getattr(self._agent_loop, "model", "") or ""
        return AgentRuntimeView(
            agentId="default",
            model=model,
            state=state,
            activeSessions=active_count,
            queueDepth=queue_depth,
            updatedAt=datetime.now(),
        )

    def set_channel_paused(self, channel_id: str, paused: bool) -> None:
        """Mark channel as paused (control-plane state; dispatch respects it)."""
        if paused:
            self._paused_channel_ids.add(channel_id)
        else:
            self._paused_channel_ids.discard(channel_id)

    def is_channel_paused(self, channel_id: str) -> bool:
        """Return whether channel is currently paused."""
        return channel_id in self._paused_channel_ids

    def get_paused_channel_ids(self) -> set[str]:
        """Return set of paused channel ids (for outbound dispatch check)."""
        return set(self._paused_channel_ids)

    def get_session_messages(self, session_key: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return last N messages for a session (for dashboard chat timeline)."""
        if not self._session_manager:
            return []
        session = self._session_manager.get_or_create(session_key)
        messages = getattr(session, "messages", [])
        return list(messages[-limit:]) if messages else []
