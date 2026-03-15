"""Append-only control-plane event log with replay and idempotent apply."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from nanobot.config.paths import get_control_events_dir
from nanobot.utils.helpers import ensure_dir


def _default_event_dir() -> Path:
    return ensure_dir(get_control_events_dir())


def _make_event_id() -> str:
    return str(uuid.uuid4())


class ControlEventLog:
    """
    Append-only event log for control-plane events.
    Supports append, replay (with optional eventId dedupe), and checkpoint offset.
    """

    def __init__(self, log_dir: Path | None = None):
        self._dir = log_dir or _default_event_dir()
        self._file = self._dir / "events.jsonl"
        self._seq = 0
        self._seen_ids: set[str] = set()

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def append(
        self,
        event: str,
        data: dict[str, Any],
        *,
        event_id: str | None = None,
        correlation_id: str | None = None,
        ts: datetime | None = None,
    ) -> tuple[str, int]:
        """
        Append a single event. Returns (event_id, event_seq).
        event_seq is monotonic for ordering (ts, event_seq).
        """
        eid = event_id or _make_event_id()
        seq = self._next_seq()
        ts = ts or datetime.now()
        record = {
            "_type": "event",
            "eventId": eid,
            "eventSeq": seq,
            "event": event,
            "ts": ts.isoformat(),
            "data": data,
            "correlationId": correlation_id,
        }
        self._dir.mkdir(parents=True, exist_ok=True)
        with open(self._file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return eid, seq

    def replay(
        self,
        *,
        after_seq: int = 0,
        dedupe_by_id: bool = True,
    ) -> Iterator[dict[str, Any]]:
        """
        Replay events from log. If dedupe_by_id=True, yields each eventId at most once.
        after_seq=0 means from start; otherwise first event with eventSeq > after_seq.
        """
        if not self._file.exists():
            return
        seen: set[str] = set()
        with open(self._file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("_type") != "event":
                    continue
                seq = record.get("eventSeq", 0)
                if seq <= after_seq:
                    continue
                eid = record.get("eventId", "")
                if dedupe_by_id and eid and eid in seen:
                    continue
                if dedupe_by_id and eid:
                    seen.add(eid)
                yield record

    def load_replay_sync(
        self,
        *,
        after_seq: int = 0,
        dedupe_by_id: bool = True,
    ) -> list[dict[str, Any]]:
        """Synchronous replay returning list (for projection rebuild)."""
        out: list[dict[str, Any]] = []
        if not self._file.exists():
            return out
        seen: set[str] = set()
        with open(self._file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("_type") != "event":
                    continue
                seq = record.get("eventSeq", 0)
                if seq <= after_seq:
                    continue
                eid = record.get("eventId", "")
                if dedupe_by_id and eid and eid in seen:
                    continue
                if dedupe_by_id and eid:
                    seen.add(eid)
                out.append(record)
        return out

    def last_seq(self) -> int:
        """Return the last eventSeq written (or 0)."""
        if not self._file.exists():
            return 0
        last = 0
        with open(self._file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get("_type") == "event":
                        last = max(last, record.get("eventSeq", 0))
                except json.JSONDecodeError:
                    continue
        return last

    def get_events_after(self, after_seq: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Return events with eventSeq > after_seq, ordered by eventSeq, up to limit (for backfill)."""
        out: list[dict[str, Any]] = []
        if not self._file.exists():
            return out
        with open(self._file, encoding="utf-8") as f:
            for line in f:
                if len(out) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("_type") != "event":
                    continue
                if record.get("eventSeq", 0) <= after_seq:
                    continue
                out.append(record)
        return out
