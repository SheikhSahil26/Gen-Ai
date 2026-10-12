import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"
import { CommercePanel } from "../commerce/CommercePanel"

export function AppShell({ children, recentQueries, onNewChat, onSelectRecent, onSupport, itemCount, onOpenPanel, onOpenMenu, panelProps }) {
  return <main className="app-shell">
    <Sidebar recentQueries={recentQueries} onNewChat={onNewChat} onSelectRecent={onSelectRecent} onSupport={onSupport}/>
    <section className="main-panel"><Topbar itemCount={itemCount} onOpenPanel={onOpenPanel} onOpenMenu={onOpenMenu}/>{children}</section>
    <CommercePanel {...panelProps} onOpenPanel={onOpenPanel}/>
  </main>
}
