"""FastAPI application for control plane REST and WebSocket."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from nanobot.controlplane.contracts import (
    ControlActionKind,
    ControlActionRequest,
    ControlActionResponse,
)
from nanobot.controlplane.service import ControlPlaneService


def _get_control_api_token() -> str | None:
    return os.environ.get("NANOBOT_CONTROL_API_TOKEN") or None


async def _verify_token(x_api_token: str | None = Header(None, alias="X-API-Token")) -> None:
    token = _get_control_api_token()
    if not token:
        return
    if not x_api_token or x_api_token != token:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


@asynccontextmanager
async def _lifespan(app: FastAPI):
    app.state.loop = asyncio.get_running_loop()
    svc: ControlPlaneService | None = app.state.control_service
    if svc:
        svc.rebuild_projection()
    yield
    pass


def _redact_secrets(obj: Any) -> Any:
    """Return a copy of obj with secret-like values redacted."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and isinstance(v, str) and v:
                kl = k.lower()
                if any(s in kl for s in ("secret", "token", "password")) or kl in ("apikey", "api_key"):
                    out[k] = "***"
                else:
                    out[k] = _redact_secrets(v)
            else:
                out[k] = _redact_secrets(v)
        return out
    if isinstance(obj, list):
        return [_redact_secrets(x) for x in obj]
    return obj


def create_control_app(
    service: ControlPlaneService,
    static_dir: Path | None = None,
    submit_operator_message: Callable[[str, str, str], None] | None = None,
    config_snapshot: dict[str, Any] | None = None,
) -> FastAPI:
    """Create FastAPI app with control plane routes and WS. If static_dir is set and exists, serve dashboard from it at /."""
    app = FastAPI(
        title="Nanobot Control Plane",
        lifespan=_lifespan,
    )
    app.state.control_service = service
    app.state.ws_connections: list[WebSocket] = []
    app.state.submit_operator_message = submit_operator_message
    app.state.config_snapshot = config_snapshot

    def _broadcast(event: str, data: dict[str, Any]) -> None:
        payload = {"event": event, "ts": datetime.now().isoformat(), "data": data}

        async def _send_all() -> None:
            dead = []
            for ws in app.state.ws_connections:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                try:
                    app.state.ws_connections.remove(ws)
                except ValueError:
                    pass

        try:
            loop = getattr(app.state, "loop", None)
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(_send_all(), loop)
        except Exception:
            pass

    service.set_ws_broadcast(_broadcast)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}

    # --- REST: sessions ---
    @app.get("/api/control/sessions", dependencies=[])
    async def list_sessions(
        status: str | None = Query(None),
        channel: str | None = Query(None),
        q: str | None = Query(None),
        cursor: str | None = Query(None),
        limit: int = Query(100, le=500),
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        items, next_cursor = svc.list_sessions(
            status=status, channel=channel, limit=limit, cursor=cursor
        )
        return {
            "items": [s.model_dump(by_alias=True) for s in items],
            "nextCursor": next_cursor,
        }

    @app.get("/api/control/sessions/{session_id}")
    async def get_session(
        session_id: str,
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        session = svc.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        trajectory = svc.get_trajectory_summary(session_id, limit=50)
        return {
            "session": session.model_dump(by_alias=True),
            "trajectorySummary": trajectory,
            "stats": {"turnCount": session.turn_count},
        }

    @app.get("/api/control/sessions/{session_id}/messages")
    async def get_session_messages(
        session_id: str,
        limit: int = Query(100, ge=1, le=500),
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        messages = svc.get_session_messages(session_id, limit=limit)
        return {"items": messages}

    @app.get("/api/control/sessions/{session_id}/trajectory")
    async def get_session_trajectory(
        session_id: str,
        limit: int = Query(100, ge=1, le=500),
        type_filter: str | None = Query(None, alias="type"),
        actor: str | None = Query(None),
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        steps = svc.get_trajectory_summary(session_id, limit=limit)
        if type_filter:
            steps = [s for s in steps if s.get("type") == type_filter]
        if actor:
            steps = [s for s in steps if s.get("actor") == actor]
        return {"items": steps}

    @app.post("/api/control/chat/send")
    async def chat_send(
        body: dict[str, Any],
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        session_id = body.get("sessionId") or body.get("session_id")
        content = body.get("content", "").strip()
        if not session_id or not content:
            raise HTTPException(status_code=400, detail="sessionId and content required")
        if ":" in session_id:
            channel, chat_id = session_id.split(":", 1)
        else:
            channel, chat_id = "cli", session_id
        submit = getattr(app.state, "submit_operator_message", None)
        if not submit:
            raise HTTPException(status_code=503, detail="Operator chat not available")
        try:
            submit(channel, chat_id, content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {"ok": True, "sessionId": session_id}

    # --- REST: channels ---
    @app.get("/api/control/channels")
    async def list_channels(
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        items = svc.list_channels()
        return {"items": [c.model_dump(by_alias=True) for c in items]}

    # --- REST: agents ---
    @app.get("/api/control/agents/status")
    async def get_agents_status(
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        agent = svc.get_agent_status()
        items = [agent.model_dump(by_alias=True)] if agent else []
        return {"items": items}

    # --- REST: stats ---
    @app.get("/api/control/stats/overview")
    async def get_stats_overview(
        window: int = Query(1, ge=1, le=168),
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        return svc.get_stats_overview(window_hours=window)

    @app.get("/api/control/config")
    async def get_config(
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        await _verify_token(x_api_token)
        snap = getattr(app.state, "config_snapshot", None)
        if not snap:
            return {"message": "Config not available"}
        return _redact_secrets(snap)

    @app.get("/api/control/events")
    async def get_events(
        after_seq: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> dict[str, Any]:
        """Events after cursor for backfill; deterministic by eventSeq; idempotent replay by eventId."""
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        records, last_seq = svc.get_events_after(after_seq=after_seq, limit=limit)
        return {"items": records, "lastSeq": last_seq}

    # --- REST: control actions ---
    @app.post("/api/control/channels/{channel_id}/pause", response_model=ControlActionResponse)
    async def pause_channel(
        channel_id: str,
        body: ControlActionRequest,
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> ControlActionResponse:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        return svc.execute_control_action(
            ControlActionKind.CHANNEL_PAUSE,
            channel_id,
            idempotency_key=body.idempotency_key,
            confirm_token=body.confirm_token,
            reason=body.reason,
        )

    @app.post("/api/control/channels/{channel_id}/resume", response_model=ControlActionResponse)
    async def resume_channel(
        channel_id: str,
        body: ControlActionRequest,
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> ControlActionResponse:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        return svc.execute_control_action(
            ControlActionKind.CHANNEL_RESUME,
            channel_id,
            idempotency_key=body.idempotency_key,
            confirm_token=body.confirm_token,
        )

    @app.post("/api/control/gateway/restart", response_model=ControlActionResponse)
    async def gateway_restart(
        body: ControlActionRequest,
        x_api_token: str | None = Header(None, alias="X-API-Token"),
    ) -> ControlActionResponse:
        await _verify_token(x_api_token)
        svc: ControlPlaneService = app.state.control_service
        return svc.execute_control_action(
            ControlActionKind.GATEWAY_RESTART,
            "gateway",
            idempotency_key=body.idempotency_key,
            confirm_token=body.confirm_token,
        )

    # --- WebSocket ---
    @app.websocket("/ws/control")
    async def ws_control(websocket: WebSocket) -> None:
        await websocket.accept()
        app.state.ws_connections.append(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json(
                        {"event": "pong", "ts": datetime.now().isoformat(), "data": {}}
                    )
        except WebSocketDisconnect:
            pass
        finally:
            try:
                app.state.ws_connections.remove(websocket)
            except ValueError:
                pass

    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="dashboard")

    return app
