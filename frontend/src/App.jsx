import { useMemo, useState } from "react"
import { AppShell } from "./components/layout/AppShell"
import { ChatView } from "./components/chat/ChatView"
import { useChat } from "./hooks/useChat"
import { useCommerce } from "./hooks/useCommerce"
import "./styles.css"

export default function App() {
  const chat = useChat()
  const commerce = useCommerce()
  const [tab, setTab] = useState("cart")
  const [panelOpen, setPanelOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const recentQueries = useMemo(() => chat.messages.filter(item => item.role === "user").map(item => item.content).reverse(), [chat.messages])

  async function send(message) {
    const sent = await chat.send(message)
    if (sent) {
      commerce.refresh()
      setPanelOpen(false)
    }
    return sent
  }

  const itemCount = commerce.cart?.item_count || 0
  const panelProps = {
    tab, setTab, cart: commerce.cart, orders: commerce.orders, loading: commerce.loading,
    error: commerce.error, onRefresh: commerce.refresh, onPrompt: send,
    onClose: () => setPanelOpen(false), open: panelOpen,
  }

  return <AppShell
    recentQueries={recentQueries}
    onNewChat={chat.reset}
    onSelectRecent={send}
    onSupport={() => send("I need customer support.")}
    itemCount={itemCount}
    onOpenPanel={nextTab => { if (nextTab) setTab(nextTab); setPanelOpen(true) }}
    onOpenMenu={() => setMenuOpen(true)}
    panelProps={panelProps}
  >
    <ChatView messages={chat.messages} busy={chat.busy} error={chat.error} scrollRef={chat.scrollRef} onSend={send} onDismissError={chat.clearError}/>
    {menuOpen && <div className="mobile-menu-overlay" onClick={() => setMenuOpen(false)}><div className="mobile-menu-card" onClick={event => event.stopPropagation()}><button className="mobile-menu-close" onClick={() => setMenuOpen(false)}>Close</button><p>Common Goods</p><button onClick={() => { chat.reset(); setMenuOpen(false) }}>New conversation</button><button onClick={() => { send("I need customer support."); setMenuOpen(false) }}>Contact customer support</button><button onClick={() => { setTab("cart"); setPanelOpen(true); setMenuOpen(false) }}>Your bag ({itemCount})</button><button onClick={() => { setTab("orders"); setPanelOpen(true); setMenuOpen(false) }}>Your orders</button></div></div>}
  </AppShell>
}
