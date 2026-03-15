/** REST client for control plane API */

const BASE = "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export interface SessionView {
  id: string;
  channel: string;
  chatId: string;
  status: string;
  lastActivityAt: string;
  turnCount: number;
  latestSummary?: string;
}

export interface ChannelHealthView {
  channelId: string;
  enabled: boolean;
  state: string;
  lastHeartbeatAt?: string;
  errorCount1h: number;
  note?: string;
}

export interface AgentRuntimeView {
  agentId: string;
  model: string;
  state: string;
  activeSessions: number;
  queueDepth: number;
  updatedAt: string;
}

export async function listSessions(params?: {
  status?: string;
  channel?: string;
  cursor?: string;
  limit?: number;
}): Promise<{ items: SessionView[]; nextCursor?: string }> {
  const q = new URLSearchParams();
  if (params?.status) q.set("status", params.status);
  if (params?.channel) q.set("channel", params.channel);
  if (params?.cursor) q.set("cursor", params.cursor);
  if (params?.limit) q.set("limit", String(params.limit));
  const suffix = q.toString() ? `?${q}` : "";
  return request(`/api/control/sessions${suffix}`);
}

export async function getSession(id: string): Promise<{
  session: SessionView;
  trajectorySummary: Record<string, unknown>[];
  stats: { turnCount: number };
}> {
  return request(`/api/control/sessions/${encodeURIComponent(id)}`);
}

export async function listChannels(): Promise<{ items: ChannelHealthView[] }> {
  return request("/api/control/channels");
}

export async function getAgentsStatus(): Promise<{ items: AgentRuntimeView[] }> {
  return request("/api/control/agents/status");
}

export async function getStatsOverview(window?: number): Promise<{
  sessions: number;
  errors: number;
  latency: number | null;
  throughput: number | null;
  window: string;
}> {
  const suffix = window != null ? `?window=${window}` : "";
  return request(`/api/control/stats/overview${suffix}`);
}

export async function getEventsAfter(afterSeq: number, limit = 100): Promise<{
  items: { eventId: string; eventSeq: number; event: string; ts: string; data: Record<string, unknown> }[];
  lastSeq: number;
}> {
  return request(`/api/control/events?after_seq=${afterSeq}&limit=${limit}`);
}

export async function pauseChannel(
  channelId: string,
  body: { idempotencyKey: string; confirmToken?: string; reason?: string }
): Promise<{ actionId: string; result: string; state?: string; error?: string }> {
  return request(`/api/control/channels/${encodeURIComponent(channelId)}/pause`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function resumeChannel(
  channelId: string,
  body: { idempotencyKey: string; confirmToken?: string }
): Promise<{ actionId: string; result: string; state?: string; error?: string }> {
  return request(`/api/control/channels/${encodeURIComponent(channelId)}/resume`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface ChatMessage {
  role: string;
  content: string;
  timestamp?: string;
  tool_calls?: unknown;
  name?: string;
}

export async function getSessionMessages(
  sessionId: string,
  limit?: number
): Promise<{ items: ChatMessage[] }> {
  const q = limit != null ? `?limit=${limit}` : "";
  return request(`/api/control/sessions/${encodeURIComponent(sessionId)}/messages${q}`);
}

export async function sendChatMessage(sessionId: string, content: string): Promise<{ ok: boolean; sessionId: string }> {
  return request("/api/control/chat/send", {
    method: "POST",
    body: JSON.stringify({ sessionId, content }),
  });
}

export interface TrajectoryStep {
  eventId?: string;
  ts?: string;
  sessionId?: string;
  type?: string;
  actor?: string;
  payload?: Record<string, unknown>;
  correlationId?: string;
  eventSeq?: number;
}

export async function getSessionTrajectory(
  sessionId: string,
  params?: { limit?: number; type?: string; actor?: string }
): Promise<{ items: TrajectoryStep[] }> {
  const q = new URLSearchParams();
  if (params?.limit != null) q.set("limit", String(params.limit));
  if (params?.type) q.set("type", params.type);
  if (params?.actor) q.set("actor", params.actor);
  const suffix = q.toString() ? `?${q}` : "";
  return request(`/api/control/sessions/${encodeURIComponent(sessionId)}/trajectory${suffix}`);
}

export async function getConfig(): Promise<Record<string, unknown>> {
  return request("/api/control/config");
}

export async function gatewayRestart(body: {
  idempotencyKey: string;
  confirmToken?: string;
}): Promise<{ actionId: string; result: string; state?: string; error?: string }> {
  return request("/api/control/gateway/restart", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
