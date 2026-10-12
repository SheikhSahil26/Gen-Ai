import { AlertCircle } from "lucide-react"
import { ChatComposer } from "./ChatComposer"
import { ChatMessage } from "./ChatMessage"
import { StarterPrompts } from "./StarterPrompts"

export function ChatView({ messages, busy, error, scrollRef, onSend, onDismissError }) {
  const isNew = messages.length === 1
  return <section className="chat-column">
    <div className="chat-scroll" ref={scrollRef}>
      <div className="chat-inner">
        {isNew && <div className="hero-intro"><div className="eyebrow"><span/> THE BETTER WAY TO FIND IT</div><h1>Good things<br/><em>start here.</em></h1><p>Tell me what you have in mind. I’ll help you find something you’ll love.</p></div>}
        <div className="messages" aria-live="polite">
          {messages.map(message => <ChatMessage key={message.id} message={message} onSend={onSend} busy={busy}/>)}
          {busy && <div className="typing-row"><span className="assistant-avatar"><i className="brand-dot"/></span><div><div className="message-label">COMMON GOODS <span>·</span> SHOPPING ASSISTANT</div><div className="typing-bubble"><i/><i/><i/></div></div></div>}
          {error && <div className="error-banner" role="alert"><AlertCircle size={16}/><span>{error}</span><button onClick={onDismissError}>Dismiss</button></div>}
        </div>
        {isNew && <StarterPrompts onChoose={onSend}/>}
      </div>
    </div>
    <ChatComposer busy={busy} onSend={onSend}/>
  </section>
}
