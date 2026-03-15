import React, { useEffect, useState } from "react";
import * as api from "../../api";
import type { AgentRuntimeView } from "../../api";

export function AgentsPage() {
  const [items, setItems] = useState<AgentRuntimeView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getAgentsStatus()
      .then((r) => { setItems(r.items); setError(null); })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><h1>Agents</h1><div className="card"><p>Loading…</p></div></div>;
  if (error) return <div className="page"><h1>Agents</h1><div className="card"><p className="error">{error}</p></div></div>;

  return (
    <div className="page">
      <h1>Agents</h1>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Model</th>
              <th>State</th>
              <th>Active sessions</th>
              <th>Queue</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr><td colSpan={5}>No agents</td></tr>
            ) : (
              items.map((a) => (
                <tr key={a.agentId}>
                  <td>{a.agentId}</td>
                  <td>{a.model}</td>
                  <td><span className={`badge ${a.state}`}>{a.state}</span></td>
                  <td>{a.activeSessions}</td>
                  <td>{a.queueDepth}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
