import React, { useEffect, useState } from "react";
import * as api from "../../api";

export function ConfigPage() {
  const [config, setConfig] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getConfig()
      .then(setConfig)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <div className="page"><h1>Config</h1><div className="card"><p className="error">{error}</p></div></div>;
  if (!config) return <div className="page"><h1>Config</h1><div className="card"><p>Loading…</p></div></div>;
  if ("message" in config) return <div className="page"><h1>Config</h1><div className="card"><p className="muted">{String(config.message)}</p></div></div>;

  return (
    <div className="page">
      <h1>Config</h1>
      <p className="muted">Read-only view. Secret values are redacted. Edits require guarded write (Phase 4).</p>
      <div className="card">
        <pre className="config-json">{JSON.stringify(config, null, 2)}</pre>
      </div>
    </div>
  );
}
