import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../../api";
import type { SessionView } from "../../api";

export function SessionsPage() {
  const [items, setItems] = useState<SessionView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listSessions({ limit: 50 })
      .then((r) => { setItems(r.items); setError(null); })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><h1>Sessions</h1><div className="card"><p>Loading…</p></div></div>;
  if (error) return <div className="page"><h1>Sessions</h1><div className="card"><p className="error">{error}</p></div></div>;

  return (
    <div className="page">
      <h1>Sessions</h1>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Channel</th>
              <th>Status</th>
              <th>Turns</th>
              <th>Last activity</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr><td colSpan={5}>No sessions</td></tr>
            ) : (
              items.map((s) => (
                <tr key={s.id}>
                  <td><Link to={`/control/sessions/${encodeURIComponent(s.id)}`}>{s.id}</Link></td>
                  <td>{s.channel}</td>
                  <td>{s.status}</td>
                  <td>{s.turnCount}</td>
                  <td>{s.lastActivityAt.slice(0, 19)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
