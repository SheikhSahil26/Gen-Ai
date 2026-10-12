import { ArrowRight, RefreshCw, ShoppingBag } from "lucide-react"
import { formatMoney } from "../../utils/format"

export function CartPanel({ cart, loading, error, onRefresh, onShop }) {
  const items = cart?.items || []
  return <section className="commerce-content">
    <div className="panel-heading"><div><span className="panel-eyebrow">YOUR SELECTION</span><h2>Your bag <span>{cart?.item_count || 0}</span></h2></div><button className="icon-button subtle" onClick={onRefresh} aria-label="Refresh cart"><RefreshCw size={15}/></button></div>
    {error && <div className="panel-error">{error}</div>}
    {loading && !cart ? <PanelLoading/> : items.length === 0 ? <div className="empty-state"><span className="empty-icon"><ShoppingBag size={19}/></span><strong>Your bag is taking a breather</strong><p>Ask the assistant to find something and add it to your cart.</p><button onClick={onShop}>Explore products <ArrowRight size={14}/></button></div> : <>
      <div className="cart-items">{items.map(item => <article className="cart-item" key={item.cart_item_id}><div className="item-thumb"><span>{(item.product_name || "G").slice(0, 1).toUpperCase()}</span></div><div className="cart-item-info"><strong>{item.product_name}</strong><span>{item.variant_name}</span><span>Qty {item.quantity}</span><div className="cart-item-price"><b>{formatMoney(item.total_after_discount, cart.currency)}</b>{Number(item.discount_total) > 0 && <del>{formatMoney(item.line_total, cart.currency)}</del>}</div></div></article>)}</div>
      <div className="cart-summary"><div><span>Subtotal</span><b>{formatMoney(cart.subtotal, cart.currency)}</b></div>{Number(cart.discount) > 0 && <div className="discount-row"><span>You saved</span><b>−{formatMoney(cart.discount, cart.currency)}</b></div>}<div className="cart-total"><span>Estimated total</span><b>{formatMoney(cart.total, cart.currency)}</b></div><p>Shipping and taxes are confirmed at checkout.</p><button className="checkout-chat-button" onClick={() => onShop("I want to check out my cart")}>Continue to checkout <ArrowRight size={15}/></button></div>
    </>}
  </section>
}

function PanelLoading() { return <div className="panel-loading"><span className="spinner muted-spinner"/> Loading your details…</div> }
