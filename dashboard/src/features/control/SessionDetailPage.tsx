import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import * as api from "../../api";

export function SessionDetailPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [data, setData] = useState<{
    session: api.SessionView;
    trajectorySummary: Record<string, unknown>[];
    stats: { turnCount: number };
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    api.getSession(decodeURIComponent(sessionId))
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [sessionId]);

  if (!sessionId) return <div className="page"><p>Missing session ID</p></div>;
  if (error) return <div className="page"><p className="error">{error}</p></div>;
  if (!data) return <div className="page"><h1>Session</h1><div className="card"><p>Loading…</p></div></div>;

  const { session, trajectorySummary, stats } = data;
  const traj = Array.isArray(trajectorySummary) ? trajectorySummary : [];

  return (
    <div className="page">
      <h1>Session <Link to="/control/sessions">←</Link> {session.id}</h1>
      <div className="card">
        <p><strong>Channel</strong> {session.channel} | <strong>Chat</strong> {session.chatId} | <strong>Status</strong> {session.status} | <strong>Turns</strong> {stats.turnCount}</p>
        <h2>Trajectory (last 30)</h2>
        <table>
          <thead>
            <tr><th>Event</th><th>Type</th><th>Actor</th><th>Payload</th></tr>
          </thead>
          <tbody>
            {traj.length === 0 ? (
              <tr><td colSpan={4}>No events</td></tr>
            ) : (
              traj.slice(-30).reverse().map((t, i) => (
                <tr key={i}>
                  <td>{String(t.eventId ?? "")}</td>
                  <td>{String(t.type ?? "")}</td>
                  <td>{String(t.actor ?? "")}</td>
                  <td>{JSON.stringify(t.payload ?? {}).slice(0, 80)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
