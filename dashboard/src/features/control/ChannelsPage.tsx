import React, { useEffect, useState } from "react";
import * as api from "../../api";
import type { ChannelHealthView } from "../../api";

export function ChannelsPage() {
  const [items, setItems] = useState<ChannelHealthView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    api.listChannels()
      .then((r) => { setItems(r.items); setError(null); })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(() => load(), []);

  const handlePause = (channelId: string) => {
    api.pauseChannel(channelId, { idempotencyKey: crypto.randomUUID() }).then(load).catch((e) => alert(String(e)));
  };
  const handleResume = (channelId: string) => {
    api.resumeChannel(channelId, { idempotencyKey: crypto.randomUUID() }).then(load).catch((e) => alert(String(e)));
  };

  if (loading) return <div className="page"><h1>Channels</h1><div className="card"><p>Loading…</p></div></div>;
  if (error) return <div className="page"><h1>Channels</h1><div className="card"><p className="error">{error}</p></div></div>;

  return (
    <div className="page">
      <h1>Channels</h1>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Channel</th>
              <th>State</th>
              <th>Enabled</th>
              <th>Errors (1h)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr><td colSpan={5}>No channels</td></tr>
            ) : (
              items.map((c) => (
                <tr key={c.channelId}>
                  <td>{c.channelId}</td>
                  <td><span className={`badge ${c.state}`}>{c.state}</span></td>
                  <td>{c.enabled ? "Yes" : "No"}</td>
                  <td>{c.errorCount1h}</td>
                  <td>
                    {c.state === "paused" ? (
                      <button type="button" onClick={() => handleResume(c.channelId)}>Resume</button>
                    ) : (
                      <button type="button" onClick={() => handlePause(c.channelId)}>Pause</button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
