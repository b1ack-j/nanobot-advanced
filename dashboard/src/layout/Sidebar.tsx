import { NavLink } from "react-router-dom";

const nav = [
  { label: "Chat", path: "/chat", icon: "💬" },
  {
    label: "Control",
    children: [
      { label: "Overview", path: "/control/overview", icon: "📊" },
      { label: "Channels", path: "/control/channels", icon: "🔗" },
      { label: "Sessions", path: "/control/sessions", icon: "📄" },
      { label: "Usage", path: "/control/usage", icon: "📈" },
    ],
  },
  {
    label: "Trajectory",
    children: [
      { label: "Timeline", path: "/trajectory", icon: "🕐" },
    ],
  },
  {
    label: "Agent",
    children: [
      { label: "Agents", path: "/agent/agents", icon: "📁" },
      { label: "Skills", path: "/agent/skills", icon: "⚡" },
      { label: "Nodes", path: "/agent/nodes", icon: "🔲" },
    ],
  },
  {
    label: "Settings",
    children: [
      { label: "Config", path: "/settings/config", icon: "⚙️" },
      { label: "Debug", path: "/settings/debug", icon: "🐛" },
      { label: "Logs", path: "/settings/logs", icon: "📜" },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">Nanobot Control</div>
      <nav className="sidebar-nav">
        {nav.map((item) => (
          <div key={item.label}>
            {"path" in item ? (
              <NavLink
                to={item.path as string}
                className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
              >
                <span className="sidebar-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ) : (
              <>
                <div className="sidebar-group">{item.label}</div>
                {"children" in item &&
                  item.children.map((child) => (
                    <NavLink
                      key={child.path}
                      to={child.path as string}
                      className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
                    >
                      <span className="sidebar-icon">{child.icon}</span>
                      {child.label}
                    </NavLink>
                  ))}
              </>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
