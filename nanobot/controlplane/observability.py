"""Observability correctness checks: event ordering, projection consistency."""

from __future__ import annotations

from pathlib import Path

from nanobot.controlplane.eventlog import ControlEventLog


def check_event_log_ordering(log_dir: Path | None = None) -> tuple[bool, str]:
    """
    Verify event log has monotonic eventSeq and no duplicate eventId in order.
    Returns (ok, message).
    """
    log = ControlEventLog(log_dir)
    if not log._file.exists():
        return True, "No event log"
    seen_seq: set[int] = set()
    seen_id: set[str] = set()
    last_seq = 0
    with open(log._file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                import json
                record = json.loads(line)
            except Exception:
                continue
            if record.get("_type") != "event":
                continue
            seq = record.get("eventSeq", 0)
            eid = record.get("eventId", "")
            if seq in seen_seq:
                return False, f"Duplicate eventSeq {seq}"
            if eid and eid in seen_id:
                return False, f"Duplicate eventId {eid}"
            if seq < last_seq:
                return False, f"EventSeq out of order: {seq} < {last_seq}"
            seen_seq.add(seq)
            if eid:
                seen_id.add(eid)
            last_seq = seq
    return True, f"OK: {last_seq} events ordered"


def check_projection_rebuild_idempotent(
    event_log: ControlEventLog, workspace: Path
) -> tuple[bool, str]:
    """
    Rebuild projection twice from same log; state should be deterministic.
    Returns (ok, message). Does not assert full equality of in-memory state;
    just ensures replay completes without error and last_applied_seq is consistent.
    """
    from nanobot.controlplane.projection import ProjectionIndex

    proj1 = ProjectionIndex(event_log, workspace)
    proj2 = ProjectionIndex(event_log, workspace)
    proj1.rebuild()
    proj2.rebuild()
    if proj1.last_applied_seq() != proj2.last_applied_seq():
        return False, f"last_applied_seq mismatch: {proj1.last_applied_seq()} vs {proj2.last_applied_seq()}"
    return True, f"OK: last_seq={proj1.last_applied_seq()}"
