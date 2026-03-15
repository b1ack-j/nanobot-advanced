import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function Layout({ children }: { children?: React.ReactNode }) {
  return (
    <div className="layout">
      <Sidebar />
      <div className="main">
        <Header />
        <div className="content">
          {children ?? <Outlet />}
        </div>
      </div>
    </div>
  );
}
