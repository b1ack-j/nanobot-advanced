/** WebSocket client for control plane live updates. On reconnect, use backfill (get_events_after(lastSeq)) to catch up. */

const WS_BASE = ((): string => {
  const u = typeof location !== "undefined" ? location : { protocol: "http:", host: "localhost:18790" };
  return (u.protocol === "https:" ? "wss:" : "ws:") + "//" + u.host;
})();

const LAST_SEQ_KEY = "nanobot_control_last_seq";

export type WsHandler = (event: string, data: Record<string, unknown>) => void;

let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
const handlers: Set<WsHandler> = new Set();
const RECONNECT_MS = 3000;

export function getStoredLastSeq(): number {
  try {
    const s = localStorage.getItem(LAST_SEQ_KEY);
    return s ? Math.max(0, parseInt(s, 10)) : 0;
  } catch {
    return 0;
  }
}

export function setStoredLastSeq(seq: number): void {
  try {
    localStorage.setItem(LAST_SEQ_KEY, String(seq));
  } catch {
    /* ignore */
  }
}

function connect(): void {
  if (ws?.readyState === WebSocket.OPEN) return;
  const url = `${WS_BASE}/ws/control`;
  ws = new WebSocket(url);
  ws.onopen = () => {
    handlers.forEach((h) => h("_connected", {}));
  };
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data as string) as { event?: string; data?: Record<string, unknown>; ts?: string };
      const event = msg.event ?? "unknown";
      const data = msg.data ?? {};
      const seq = (data as { eventSeq?: number }).eventSeq;
      if (typeof seq === "number") setStoredLastSeq(seq);
      handlers.forEach((h) => h(event, data));
    } catch {
      // ignore parse errors
    }
  };
  ws.onclose = () => {
    ws = null;
    handlers.forEach((h) => h("_disconnected", {}));
    reconnectTimer = setTimeout(connect, RECONNECT_MS);
  };
  ws.onerror = () => {};
}

export function subscribe(handler: WsHandler): () => void {
  handlers.add(handler);
  if (!ws || ws.readyState !== WebSocket.OPEN) connect();
  return () => {
    handlers.delete(handler);
  };
}

export function isConnected(): boolean {
  return ws?.readyState === WebSocket.OPEN;
}
