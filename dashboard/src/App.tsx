import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./layout/Layout";
import { ChatPage } from "./features/chat/ChatPage";
import { OverviewPage } from "./features/control/OverviewPage";
import { ChannelsPage } from "./features/control/ChannelsPage";
import { SessionsPage } from "./features/control/SessionsPage";
import { UsagePage } from "./features/control/UsagePage";
import { AgentsPage } from "./features/agent/AgentsPage";
import { SkillsPage } from "./features/agent/SkillsPage";
import { NodesPage } from "./features/agent/NodesPage";
import { ConfigPage } from "./features/settings/ConfigPage";
import { DebugPage } from "./features/settings/DebugPage";
import { LogsPage } from "./features/settings/LogsPage";
import { TrajectoryPage } from "./features/trajectory/TrajectoryPage";
import { SessionDetailPage } from "./features/control/SessionDetailPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/control/overview" element={<OverviewPage />} />
        <Route path="/control/channels" element={<ChannelsPage />} />
        <Route path="/control/sessions" element={<SessionsPage />} />
        <Route path="/control/sessions/:sessionId" element={<SessionDetailPage />} />
        <Route path="/control/usage" element={<UsagePage />} />
        <Route path="/trajectory" element={<TrajectoryPage />} />
        <Route path="/agent/agents" element={<AgentsPage />} />
        <Route path="/agent/skills" element={<SkillsPage />} />
        <Route path="/agent/nodes" element={<NodesPage />} />
        <Route path="/settings/config" element={<ConfigPage />} />
        <Route path="/settings/debug" element={<DebugPage />} />
        <Route path="/settings/logs" element={<LogsPage />} />
      </Routes>
    </Layout>
  );
}
