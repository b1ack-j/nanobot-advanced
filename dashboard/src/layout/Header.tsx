import { useAppStore } from "../store/AppStore";

export function Header() {
  const { wsState } = useAppStore();
  return (
    <header className="header">
      <span className="header-spacer" />
      <span className={`ws-status ${wsState === "connected" ? "connected" : ""}`}>
        {wsState === "connected" ? "● Live" : wsState === "connecting" ? "○ Connecting…" : "○ Disconnected"}
      </span>
    </header>
  );
}
