import React, { useEffect, useState } from "react";
import * as api from "../../api";

export function OverviewPage() {
  const [stats, setStats] = useState<{ sessions: number; errors: number; window: string } | null>(null);
  const [agents, setAgents] = useState<api.AgentRuntimeView[]>([]);
  const [channels, setChannels] = useState<api.ChannelHealthView[]>([]);
  const [restarting, setRestarting] = useState(false);
  const [restartConfirm, setRestartConfirm] = useState("");
  const [restartError, setRestartError] = useState<string | null>(null);

  const load = () => {
    api.getStatsOverview(1).then(setStats).catch(() => setStats({ sessions: 0, errors: 0, window: "1h" }));
    api.getAgentsStatus().then((r) => setAgents(r.items)).catch(() => setAgents([]));
    api.listChannels().then((r) => setChannels(r.items)).catch(() => setChannels([]));
  };

  useEffect(() => load(), []);

  const handleRestart = () => {
    if (restartConfirm !== "restart") return;
    setRestartError(null);
    setRestarting(true);
    api
      .gatewayRestart({ idempotencyKey: crypto.randomUUID(), confirmToken: undefined })
      .then(() => {
        setRestartConfirm("");
      })
      .catch((e) => setRestartError(String(e)))
      .finally(() => setRestarting(false));
  };

  const queueDepth = agents[0]?.queueDepth ?? 0;
  const channelCount = channels.length;
  const healthyChannels = channels.filter((c) => c.state === "healthy" || c.state === "running").length;

  return (
    <div className="page">
      <h1>Overview</h1>
      <div className="card grid2">
        <div><strong>Sessions</strong> {stats?.sessions ?? "—"}</div>
        <div><strong>Errors</strong> {stats?.errors ?? "—"}</div>
        <div><strong>Window</strong> {stats?.window ?? "—"}</div>
        <div><strong>Queue depth</strong> {queueDepth}</div>
        <div><strong>Channels</strong> {healthyChannels}/{channelCount || "—"}</div>
      </div>

      <div className="card">
        <h2>Gateway</h2>
        <p className="muted">Restart gateway (safety-gated). Type &quot;restart&quot; to confirm.</p>
        <div className="gateway-restart">
          <input
            type="text"
            placeholder="Type restart to confirm"
            value={restartConfirm}
            onChange={(e) => setRestartConfirm(e.target.value)}
            disabled={restarting}
          />
          <button
            type="button"
            onClick={handleRestart}
            disabled={restartConfirm !== "restart" || restarting}
          >
            {restarting ? "Sending…" : "Restart gateway"}
          </button>
        </div>
        {restartError && <p className="error">{restartError}</p>}
      </div>
    </div>
  );
}
