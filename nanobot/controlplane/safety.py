"""Confirmation, idempotency, and audit enforcement for control actions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from nanobot.controlplane.contracts import ControlActionKind, ControlActionResult


# Actions that require explicit confirmation token
REQUIRE_CONFIRM: set[ControlActionKind] = {
    ControlActionKind.GATEWAY_RESTART,
    ControlActionKind.CHANNEL_PAUSE,
    ControlActionKind.CHANNEL_RESUME,
}


class SafetyGate:
    """
    Validates confirmation token for sensitive actions and dedupes by idempotency key.
    """

    def __init__(self, *, expected_confirm_token: str | None = None):
        self._expected_token = expected_confirm_token or ""
        self._idempotency_cache: dict[str, dict[str, Any]] = {}

    def validate_confirm(self, kind: ControlActionKind, confirm_token: str | None) -> str | None:
        """
        Return None if valid; else error message.
        If kind requires confirm, confirm_token must match expected.
        """
        if kind not in REQUIRE_CONFIRM:
            return None
        if not self._expected_token:
            return None  # no token configured => no check
        if not confirm_token or confirm_token != self._expected_token:
            return "Confirmation token required and must match"
        return None

    def get_cached_result(self, idempotency_key: str) -> dict[str, Any] | None:
        """Return cached result for this idempotency key if any."""
        return self._idempotency_cache.get(idempotency_key)

    def cache_result(
        self,
        idempotency_key: str,
        result: ControlActionResult,
        *,
        action_id: str | None = None,
        state: str | None = None,
        error: str | None = None,
    ) -> None:
        """Store result for idempotency (same key returns same result)."""
        self._idempotency_cache[idempotency_key] = {
            "actionId": action_id or idempotency_key,
            "result": result.value,
            "state": state,
            "error": error,
            "cached_at": datetime.now().isoformat(),
        }
        # Bound cache size
        if len(self._idempotency_cache) > 1000:
            oldest = min(
                self._idempotency_cache.keys(),
                key=lambda k: self._idempotency_cache[k].get("cached_at", ""),
            )
            self._idempotency_cache.pop(oldest, None)

    def requires_confirm(self, kind: ControlActionKind) -> bool:
        return kind in REQUIRE_CONFIRM
