import { BadgeCheck, X } from "lucide-react"

export function CheckoutApproval({ onConfirm, onCancel, disabled }) {
  return <div className="approval-card">
    <div className="approval-heading"><span className="approval-icon"><BadgeCheck size={17}/></span><div><strong>Ready to place your order?</strong><span>Review the order details above before confirming.</span></div></div>
    <div className="approval-actions"><button className="confirm-button" disabled={disabled} onClick={onConfirm}>Confirm &amp; place order</button><button className="cancel-button" disabled={disabled} onClick={onCancel}><X size={14}/> Cancel</button></div>
  </div>
}
