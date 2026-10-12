import { Menu, Package, ShoppingBag, Sparkles } from "lucide-react"

export function Topbar({ itemCount, onOpenPanel, onOpenMenu }) {
  return <header className="topbar">
    <button className="icon-button mobile-only" aria-label="Open navigation" onClick={onOpenMenu}><Menu size={19}/></button>
    <div className="crumbs"><span>Discover</span><span className="crumb-divider">/</span><strong><Sparkles size={14}/> Shopping assistant</strong></div>
    <div className="topbar-actions"><span className="online-label"><i/> Personal shopping guide</span>
      <button className="topbar-action mobile-only" onClick={() => onOpenPanel("orders")} aria-label="Open orders"><Package size={17}/></button>
      <button className="topbar-action" onClick={() => onOpenPanel("cart")} aria-label={`Open cart, ${itemCount} items`}><ShoppingBag size={17}/><span>Bag</span><b>{itemCount}</b></button>
    </div>
  </header>
}
