import React, { useCallback, useEffect, useState } from "react";
import { useAppStore } from "../../store/AppStore";
import * as api from "../../api";
import type { TrajectoryStep } from "../../api";

export function TrajectoryPage() {
  const { sessions } = useAppStore();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [items, setItems] = useState<TrajectoryStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [actorFilter, setActorFilter] = useState<string>("");

  const load = useCallback(() => {
    if (!sessionId) {
      setItems([]);
      return;
    }
    setLoading(true);
    api
      .getSessionTrajectory(sessionId, {
        limit: 150,
        type: typeFilter || undefined,
        actor: actorFilter || undefined,
      })
      .then((r) => setItems(r.items))
      .finally(() => setLoading(false));
  }, [sessionId, typeFilter, actorFilter]);

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [load]);

  useEffect(() => {
    if (!sessionId && sessions[0]) setSessionId(sessions[0].id);
  }, [sessions, sessionId]);

  const turnEvents = items.filter((e) => e.type === "turn.started" || e.type === "turn.completed");
  const toolEvents = items.filter((e) => e.type === "tool.invoked" || e.type === "tool.completed");

  return (
    <div className="page">
      <h1>Trajectory</h1>
      <p className="muted">Observe chat trajectory and tool/skill calls per session.</p>

      <div className="trajectory-toolbar">
        <label>
          Session{" "}
          <select
            value={sessionId ?? ""}
            onChange={(e) => setSessionId(e.target.value || null)}
          >
            <option value="">— Select —</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id}
              </option>
            ))}
          </select>
        </label>
        <label>
          Type{" "}
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">All</option>
            <option value="turn.started">turn.started</option>
            <option value="turn.completed">turn.completed</option>
            <option value="tool.invoked">tool.invoked</option>
            <option value="tool.completed">tool.completed</option>
          </select>
        </label>
        <label>
          Actor{" "}
          <select value={actorFilter} onChange={(e) => setActorFilter(e.target.value)}>
            <option value="">All</option>
            <option value="user">user</option>
            <option value="assistant">assistant</option>
            <option value="system">system</option>
          </select>
        </label>
        <button type="button" onClick={load} disabled={loading}>
          Refresh
        </button>
      </div>

      {!sessionId ? (
        <div className="card">
          <p className="muted">Select a session to view trajectory.</p>
        </div>
      ) : (
        <div className="trajectory-timeline">
          <div className="card">
            <h2>Turn lane</h2>
            <ul className="trajectory-list">
              {turnEvents.length === 0 ? (
                <li className="muted">No turn events</li>
              ) : (
                turnEvents.map((e, i) => (
                  <li key={e.eventId ?? i} className={`traj-event traj-${(e.type ?? "").replace(".", "-")}`}>
                    <span className="traj-ts">{e.ts?.slice(11, 19) ?? ""}</span>
                    <span className="traj-type">{e.type}</span>
                    <span className="traj-actor">{e.actor}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
          <div className="card">
            <h2>Tool lane</h2>
            <ul className="trajectory-list">
              {toolEvents.length === 0 ? (
                <li className="muted">No tool events</li>
              ) : (
                toolEvents.map((e, i) => (
                  <li key={e.eventId ?? i} className={`traj-event traj-${(e.type ?? "").replace(".", "-")}`}>
                    <span className="traj-ts">{e.ts?.slice(11, 19) ?? ""}</span>
                    <span className="traj-type">{e.type}</span>
                    <span className="traj-tool">
                      {(e.payload as { name?: string })?.name ?? "—"}
                    </span>
                    {e.type === "tool.completed" && (
                      <span className="traj-preview">
                        {String((e.payload as { result_preview?: string })?.result_preview ?? "").slice(0, 80)}
                      </span>
                    )}
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
