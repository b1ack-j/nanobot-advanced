import React, { useCallback, useEffect, useRef, useState } from "react";
import { useAppStore } from "../../store/AppStore";
import * as api from "../../api";
import type { ChatMessage } from "../../api";
import { subscribe } from "../../ws";

/** Message with optional client-side id for optimistic updates */
type MessageItem = ChatMessage & { id?: string };

/** Live agent status from trajectory.step */
type AgentStatus =
  | { kind: "thinking" }
  | { kind: "tool"; toolName: string }
  | { kind: "tool-done"; toolName: string }
  | null;

export function ChatPage() {
  const { sessions, activeSessionId, setActiveSessionId, refreshSessions } = useAppStore();
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [optimisticQueue, setOptimisticQueue] = useState<MessageItem[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLLIElement>(null);
  const chatMessagesRef = useRef<HTMLDivElement>(null);

  const sessionId = activeSessionId ?? (sessions[0]?.id ?? null);

  const displayMessages: MessageItem[] = [...messages, ...optimisticQueue];

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [displayMessages.length, agentStatus, scrollToBottom]);

  const loadMessages = useCallback(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    setError(null);
    api
      .getSessionMessages(sessionId, 100)
      .then((r) => {
        const items = r.items as MessageItem[];
        setMessages(items);
        if (items.length === 0) {
          setOptimisticQueue([]);
          return;
        }
        setOptimisticQueue((pending) => {
          const lastUserMessage = [...items].reverse().find((m) => m.role === "user");
          const lastUserContent = lastUserMessage
            ? String(lastUserMessage.content).trim()
            : null;
          return pending.filter((p) => {
            const c = String(p.content).trim();
            return c !== lastUserContent;
          });
        });
      })
      .catch((e) => setError(String(e)));
  }, [sessionId]);

  useEffect(() => {
    loadMessages();
    const t = setInterval(loadMessages, 3000);
    return () => clearInterval(t);
  }, [loadMessages]);

  useEffect(() => {
    if (!activeSessionId && sessions[0]) setActiveSessionId(sessions[0].id);
  }, [sessions, activeSessionId, setActiveSessionId]);

  useEffect(() => {
    if (!sessionId) return;
    const unsub = subscribe((event, data) => {
      const sid =
        (data as { sessionId?: string }).sessionId ??
        (data as { session_id?: string }).session_id;
      if (sid !== sessionId) return;

      if (event === "session.updated") {
        loadMessages();
        return;
      }

      if (event === "trajectory.step") {
        const stepType = (data as { type?: string }).type ?? "";
        const payload = (data as { payload?: { name?: string } }).payload ?? {};
        const toolName = payload.name ?? "";

        if (stepType === "turn.started") {
          setAgentStatus({ kind: "thinking" });
        } else if (stepType === "tool.invoked" && toolName) {
          setAgentStatus({ kind: "tool", toolName });
        } else if (stepType === "tool.completed" && toolName) {
          setAgentStatus({ kind: "tool-done", toolName });
        } else if (stepType === "turn.completed") {
          setAgentStatus(null);
          loadMessages();
        }
      }
    });
    return unsub;
  }, [sessionId, loadMessages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || !sessionId || sending) return;
    const optimistic: MessageItem = {
      role: "user",
      content: text,
      id: `pending-${Date.now()}`,
    };
    setOptimisticQueue((q) => [...q, optimistic]);
    setInput("");
    setSending(true);
    setError(null);
    api
      .sendChatMessage(sessionId, text)
      .then(() => {
        loadMessages();
      })
      .catch((e) => {
        setError(String(e));
        setOptimisticQueue((q) => q.filter((m) => m.id !== optimistic.id));
      })
      .finally(() => setSending(false));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const showStatus = agentStatus !== null;
  const statusLabel =
    agentStatus?.kind === "thinking"
      ? "Agent is thinking…"
      : agentStatus?.kind === "tool"
        ? `Calling tool: ${agentStatus.toolName}`
        : agentStatus?.kind === "tool-done"
          ? `Tool completed: ${agentStatus.toolName}`
          : null;

  return (
    <div className="page chat-page">
      <h1>Chat</h1>
      <p className="muted">Direct gateway chat session for quick interventions.</p>

      <div className="chat-toolbar">
        <label>
          Session{" "}
          <select
            value={sessionId ?? ""}
            onChange={(e) => setActiveSessionId(e.target.value || null)}
          >
            <option value="">— Select —</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id} ({s.channel})
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={() => refreshSessions()}>
          Refresh
        </button>
      </div>

      {error && <div className="card error-banner">{error}</div>}

      <div ref={chatMessagesRef} className="chat-messages">
        {!sessionId ? (
          <p className="muted">Select a session to view and send messages.</p>
        ) : displayMessages.length === 0 && !showStatus ? (
          <p className="muted">No messages yet. Send one below.</p>
        ) : (
          <ul className="message-list">
            {displayMessages.map((m, i) => (
              <li key={m.id ?? `msg-${i}`} className={`message-row message-row-${m.role}`}>
                <div className="message-bubble">
                  <div className="message-label">
                    {m.role === "user" ? "You" : "Assistant"}
                  </div>
                  <div className="message-content">
                    {typeof m.content === "string"
                      ? m.content
                      : JSON.stringify(m.content).slice(0, 200)}
                  </div>
                </div>
              </li>
            ))}
            {showStatus && statusLabel && (
              <li className="chat-status-row">
                <span
                  className={`chat-status-chip chat-status-${agentStatus?.kind ?? "thinking"}`}
                >
                  {statusLabel}
                </span>
              </li>
            )}
            <li ref={messagesEndRef} aria-hidden />
          </ul>
        )}
      </div>

      <div className="chat-send">
        <textarea
          placeholder="Message (Enter to send)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          disabled={!sessionId || sending}
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!sessionId || !input.trim() || sending}
        >
          {sending ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}
