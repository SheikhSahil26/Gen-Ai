import { Clock3, Headphones, Leaf, LogOut, Plus, Sparkles } from "lucide-react"
import { BrandMark } from "../shared/BrandMark"

export function Sidebar({ user, onLogout, recentQueries, onNewChat, onSelectRecent, onSupport }) {
  return <aside className="sidebar">
    <button className="brand" onClick={onNewChat} aria-label="Common Goods home">
      <BrandMark/><span className="brand-name">common<span>goods</span></span>
    </button>
    <button className="new-chat" onClick={onNewChat}><Plus size={16}/> New conversation</button>
    <div className="sidebar-section-label">YOUR SPACE</div>
    <div className="sidebar-active"><Sparkles size={16}/> Shopping assistant</div>
    <button className="sidebar-support" onClick={onSupport}><Headphones size={16}/><span>Customer support</span><span className="support-arrow">↗</span></button>
    {recentQueries.length > 0 && <section className="recent-section">
      <div className="sidebar-section-label">RECENT SEARCHES</div>
      {recentQueries.slice(0, 6).map((query, index) => <button key={`${query}-${index}`} className="recent-query" title={query} onClick={() => onSelectRecent(query)}><Clock3 size={14}/><span>{query}</span></button>)}
    </section>}
    <div className="sidebar-bottom">
      <div className="promise-card"><span className="promise-icon"><Leaf size={16}/></span><div><strong>Thoughtfully chosen</strong><span>Better finds, fewer tabs.</span></div></div>
      <div className="guest-profile"><span className="guest-avatar">{user?.username?.[0]?.toUpperCase() || "U"}</span><div><strong>{user?.username || "Shopper"}</strong><span>{user?.email}</span></div><button className="logout-button" onClick={onLogout} aria-label="Sign out" title="Sign out"><LogOut size={15}/></button></div>
    </div>
  </aside>
}
