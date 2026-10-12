import { ArrowUp, Sparkles } from "lucide-react"
import { useState } from "react"

export function ChatComposer({ busy, onSend }) {
  const [value, setValue] = useState("")

  async function submit(event) {
    event.preventDefault()
    const message = value.trim()
    if (!message || busy) return
    const sent = await onSend(message)
    if (sent) setValue("")
  }

  return <div className="composer-wrap"><form className="composer" onSubmit={submit}>
    <textarea aria-label="Ask the shopping assistant" rows={1} placeholder="Ask me anything about what you’re looking for…" value={value} onChange={event => setValue(event.target.value)} onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); submit(event) } }} disabled={busy}/>
    <div className="composer-footer"><span><Sparkles size={13}/> Shopping, orders, and more</span><button className="send-button" disabled={!value.trim() || busy} aria-label="Send message">{busy ? <span className="spinner"/> : <ArrowUp size={17}/>}</button></div>
  </form><p className="composer-note">Please review your order details carefully before confirming checkout.</p></div>
}
