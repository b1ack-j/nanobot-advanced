import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { SessionView, ChannelHealthView, AgentRuntimeView } from "../api";
import { subscribe, getStoredLastSeq, setStoredLastSeq } from "../ws";
import * as api from "../api";

type WsConnectionState = "connecting" | "connected" | "disconnected";

interface AppStoreState {
  wsState: WsConnectionState;
  lastSeq: number;
  sessions: SessionView[];
  channels: ChannelHealthView[];
  agents: AgentRuntimeView[];
  activeSessionId: string | null;
  eventCursor: number;
}

interface AppStoreValue extends AppStoreState {
  setActiveSessionId: (id: string | null) => void;
  refreshSessions: () => Promise<void>;
  refreshChannels: () => Promise<void>;
  refreshAgents: () => Promise<void>;
  refreshAll: () => Promise<void>;
  applyBackfill: () => Promise<void>;
}

const defaultState: AppStoreState = {
  wsState: "disconnected",
  lastSeq: getStoredLastSeq(),
  sessions: [],
  channels: [],
  agents: [],
  activeSessionId: null,
  eventCursor: 0,
};

const AppStoreContext = createContext<AppStoreValue | null>(null);

export function AppStoreProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppStoreState>(defaultState);
  const lastSeqRef = useRef(defaultState.lastSeq);

  const setActiveSessionId = useCallback((activeSessionId: string | null) => {
    setState((s) => ({ ...s, activeSessionId }));
  }, []);

  const refreshSessions = useCallback(async () => {
    try {
      const r = await api.listSessions({ limit: 100 });
      setState((s) => ({ ...s, sessions: r.items }));
    } catch {
      // keep previous
    }
  }, []);

  const refreshChannels = useCallback(async () => {
    try {
      const r = await api.listChannels();
      setState((s) => ({ ...s, channels: r.items }));
    } catch {
      // keep previous
    }
  }, []);

  const refreshAgents = useCallback(async () => {
    try {
      const r = await api.getAgentsStatus();
      setState((s) => ({ ...s, agents: r.items }));
    } catch {
      // keep previous
    }
  }, []);

  const refreshAll = useCallback(async () => {
    await Promise.all([refreshSessions(), refreshChannels(), refreshAgents()]);
  }, [refreshSessions, refreshChannels, refreshAgents]);

  const applyBackfill = useCallback(async () => {
    const after = lastSeqRef.current;
    if (after <= 0) return;
    try {
      const r = await api.getEventsAfter(after, 200);
      if (r.items.length > 0) {
        lastSeqRef.current = r.lastSeq;
        setState((s) => ({ ...s, lastSeq: r.lastSeq, eventCursor: r.lastSeq }));
        await refreshAll();
      }
    } catch {
      // ignore
    }
  }, [refreshAll]);

  useEffect(() => {
    return subscribe((event, data) => {
      if (event === "_connected") {
        setState((s) => ({ ...s, wsState: "connected" }));
        applyBackfill();
      } else if (event === "_disconnected") {
        setState((s) => ({ ...s, wsState: "disconnected" }));
      }
      const seq = (data as { eventSeq?: number }).eventSeq;
      if (typeof seq === "number") {
        setStoredLastSeq(seq);
        lastSeqRef.current = seq;
        setState((s) => ({ ...s, lastSeq: seq, eventCursor: seq }));
      }
    });
  }, [applyBackfill]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const value: AppStoreValue = {
    ...state,
    setActiveSessionId,
    refreshSessions,
    refreshChannels,
    refreshAgents,
    refreshAll,
    applyBackfill,
  };

  return (
    <AppStoreContext.Provider value={value}>
      {children}
    </AppStoreContext.Provider>
  );
}

export function useAppStore(): AppStoreValue {
  const ctx = useContext(AppStoreContext);
  if (!ctx) throw new Error("useAppStore must be used within AppStoreProvider");
  return ctx;
}
