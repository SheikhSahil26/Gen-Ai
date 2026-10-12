import { ArrowUpRight, Package, RefreshCw, Truck } from "lucide-react"
import { formatDate, formatMoney, humanize } from "../../utils/format"

export function OrdersPanel({ orders, loading, error, onRefresh, onTrack }) {
  const list = orders?.orders || []
  return <section className="commerce-content">
    <div className="panel-heading"><div><span className="panel-eyebrow">THE PAPER TRAIL</span><h2>Your orders <span>{orders?.total_orders || 0}</span></h2></div><button className="icon-button subtle" onClick={onRefresh} aria-label="Refresh orders"><RefreshCw size={15}/></button></div>
    {error && <div className="panel-error">{error}</div>}
    {loading && !orders ? <div className="panel-loading"><span className="spinner muted-spinner"/> Loading your orders…</div> : list.length === 0 ? <div className="empty-state"><span className="empty-icon"><Package size={19}/></span><strong>No orders just yet</strong><p>Your order history will show up here after checkout.</p></div> : <div className="orders-list">{list.map(order => <article className="order-card" key={order.order_number}>
      <div className="order-card-top"><div><span className="order-date">{formatDate(order.created_at)}</span><strong>{order.order_number}</strong></div><span className={`status-pill status-${(order.status || "").toLowerCase()}`}>{humanize(order.status || "processing")}</span></div>
      <div className="order-items">{(order.items || []).slice(0, 3).map((item, index) => <div key={`${item.product_name}-${index}`}><span>{item.product_name} <i>×{item.quantity}</i></span><b>{formatMoney(Number(item.unit_price) * Number(item.quantity), orders.currency)}</b></div>)}{(order.items || []).length > 3 && <small>+{order.items.length - 3} more items</small>}</div>
      <div className="order-total"><span>{order.item_count} item{order.item_count === 1 ? "" : "s"}</span><strong>{formatMoney(order.total_amount, orders.currency)}</strong></div>
      {order.tracking_number && <div className="tracking-line"><Truck size={14}/><span>{order.carrier || "Shipment"} · {order.shipment_status || "In transit"}</span></div>}
      <button className="track-order-button" onClick={() => onTrack(`Track my order ${order.order_number}`)}>Track this order <ArrowUpRight size={14}/></button>
    </article>)}</div>}
  </section>
}
