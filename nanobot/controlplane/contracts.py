"""Control-plane event, action, and query models (contracts)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# --- Enums (align with specs) ---


class SessionStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    ERROR = "error"


class ChannelState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    PAUSED = "paused"


class AgentState(str, Enum):
    RUNNING = "running"
    BUSY = "busy"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class TrajectoryEventType(str, Enum):
    TURN_STARTED = "turn.started"
    TURN_COMPLETED = "turn.completed"
    TOOL_INVOKED = "tool.invoked"
    TOOL_COMPLETED = "tool.completed"
    CONTROL_ACTION = "control.action"
    ERROR = "error"


class TrajectoryActor(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    OPERATOR = "operator"
    PLUGIN = "plugin"


class ControlActionKind(str, Enum):
    GATEWAY_RESTART = "gateway.restart"
    CHANNEL_PAUSE = "channel.pause"
    CHANNEL_RESUME = "channel.resume"
    SESSION_OPEN = "session.open"
    SESSION_MANAGE = "session.manage"
    AGENT_PAUSE = "agent.pause"
    AGENT_STOP = "agent.stop"
    AGENT_RESUME = "agent.resume"


class ControlActionResult(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class AnnotationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# --- View models (API/WS payloads) ---


class SessionView(BaseModel):
    """Session list/detail view for dashboard."""

    id: str  # channel:chat_id
    channel: str
    chat_id: str = Field(alias="chatId")
    status: SessionStatus
    last_activity_at: datetime = Field(alias="lastActivityAt")
    turn_count: int = Field(alias="turnCount", default=0)
    latest_summary: str | None = Field(alias="latestSummary", default=None)

    model_config = {"populate_by_name": True}


class ChannelHealthView(BaseModel):
    """Channel health/status for dashboard."""

    channel_id: str = Field(alias="channelId")
    enabled: bool
    state: ChannelState
    last_heartbeat_at: datetime | None = Field(alias="lastHeartbeatAt", default=None)
    error_count_1h: int = Field(alias="errorCount1h", default=0)
    note: str | None = None

    model_config = {"populate_by_name": True}


class AgentRuntimeView(BaseModel):
    """Agent runtime status for dashboard."""

    agent_id: str = Field(alias="agentId")
    model: str
    state: AgentState
    active_sessions: int = Field(alias="activeSessions", default=0)
    queue_depth: int = Field(alias="queueDepth", default=0)
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class TrajectoryEvent(BaseModel):
    """Single trajectory step (turn/tool/control) for timeline."""

    event_id: str = Field(alias="eventId")
    ts: datetime
    session_id: str = Field(alias="sessionId")
    type: TrajectoryEventType
    actor: TrajectoryActor
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = Field(alias="correlationId", default=None)
    event_seq: int = Field(alias="eventSeq", default=0)  # monotonic for ordering

    model_config = {"populate_by_name": True}


class ControlActionRecord(BaseModel):
    """Audit record for a control action."""

    action_id: str = Field(alias="actionId")
    kind: ControlActionKind
    target_id: str = Field(alias="targetId")
    requires_confirm: bool = Field(alias="requiresConfirm")
    requested_at: datetime = Field(alias="requestedAt")
    requested_by: str = Field(alias="requestedBy", default="operator")
    result: ControlActionResult

    model_config = {"populate_by_name": True}


# --- Request/response for control API ---


class ControlActionRequest(BaseModel):
    """Request body for control actions (pause/resume/restart etc)."""

    confirm_token: str | None = Field(alias="confirmToken", default=None)
    idempotency_key: str = Field(alias="idempotencyKey")
    reason: str | None = None

    model_config = {"populate_by_name": True}


class ControlActionResponse(BaseModel):
    """Response for control action endpoints."""

    action_id: str = Field(alias="actionId")
    result: ControlActionResult  # enum
    state: str | None = None  # e.g. channel state after pause
    error: str | None = None

    model_config = {"populate_by_name": True}


# --- Plugin annotation ---


class PluginAnnotation(BaseModel):
    """Annotation/alert emitted by a plugin."""

    source: str
    severity: AnnotationSeverity
    message: str
    entity_ref: dict[str, str] | None = Field(alias="entityRef", default=None)
    ts: datetime | None = None

    model_config = {"populate_by_name": True}


# --- WebSocket envelope ---


class WsEnvelope(BaseModel):
    """WebSocket message envelope (event + ts + data)."""

    event: str
    ts: datetime = Field(default_factory=datetime.now)
    data: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = Field(alias="correlationId", default=None)

    model_config = {"populate_by_name": True}
