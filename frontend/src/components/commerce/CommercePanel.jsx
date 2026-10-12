import { Package, ShoppingBag, X } from "lucide-react"
import { CartPanel } from "./CartPanel"
import { OrdersPanel } from "./OrdersPanel"

export function CommercePanel({ tab, setTab, cart, orders, loading, error, onRefresh, onPrompt, onClose, open }) {
  return <aside className={`commerce-panel ${open ? "commerce-panel-open" : ""}`}>
    <div className="commerce-mobile-head"><strong>Your account</strong><button className="icon-button" onClick={onClose} aria-label="Close panel"><X size={18}/></button></div>
    <div className="commerce-tabs" role="tablist" aria-label="Your shopping details">
      <button role="tab" aria-selected={tab === "cart"} className={tab === "cart" ? "selected" : ""} onClick={() => setTab("cart")}><ShoppingBag size={15}/> Bag <span>{cart?.item_count || 0}</span></button>
      <button role="tab" aria-selected={tab === "orders"} className={tab === "orders" ? "selected" : ""} onClick={() => setTab("orders")}><Package size={15}/> Orders <span>{orders?.total_orders || 0}</span></button>
    </div>
    {tab === "cart" ? <CartPanel cart={cart} loading={loading} error={error} onRefresh={onRefresh} onShop={onPrompt}/> : <OrdersPanel orders={orders} loading={loading} error={error} onRefresh={onRefresh} onTrack={onPrompt}/>}
  </aside>
}
