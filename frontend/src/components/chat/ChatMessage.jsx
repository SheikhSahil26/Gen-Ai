import { Check, Copy, Sparkles } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { BrandMark } from "../shared/BrandMark"
import { CheckoutApproval } from "./CheckoutApproval"

function MarkdownContent({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Tables
        table: ({ node, ...props }) => (
          <div className="md-table-wrap">
            <table className="md-table" {...props} />
          </div>
        ),
        thead: ({ node, ...props }) => <thead className="md-thead" {...props} />,
        tbody: ({ node, ...props }) => <tbody {...props} />,
        tr: ({ node, ...props }) => <tr className="md-tr" {...props} />,
        th: ({ node, ...props }) => <th className="md-th" {...props} />,
        td: ({ node, ...props }) => <td className="md-td" {...props} />,
        // Headings
        h1: ({ node, ...props }) => <h1 className="md-h1" {...props} />,
        h2: ({ node, ...props }) => <h2 className="md-h2" {...props} />,
        h3: ({ node, ...props }) => <h3 className="md-h3" {...props} />,
        // Lists
        ul: ({ node, ...props }) => <ul className="md-ul" {...props} />,
        ol: ({ node, ...props }) => <ol className="md-ol" {...props} />,
        li: ({ node, ...props }) => <li className="md-li" {...props} />,
        // Inline
        strong: ({ node, ...props }) => <strong className="md-strong" {...props} />,
        em: ({ node, ...props }) => <em className="md-em" {...props} />,
        code: ({ node, inline, ...props }) =>
          inline
            ? <code className="md-code-inline" {...props} />
            : <code className="md-code-block" {...props} />,
        pre: ({ node, ...props }) => <pre className="md-pre" {...props} />,
        blockquote: ({ node, ...props }) => <blockquote className="md-blockquote" {...props} />,
        hr: ({ node, ...props }) => <hr className="md-hr" {...props} />,
        a: ({ node, ...props }) => <a className="md-link" target="_blank" rel="noopener noreferrer" {...props} />,
        p: ({ node, ...props }) => <p className="md-p" {...props} />,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export function ChatMessage({ message, onSend, busy }) {
  const assistant = message.role === "assistant"
  return (
    <article className={`message-row ${assistant ? "assistant-message" : "user-message"}`}>
      {assistant && <div className="assistant-avatar"><BrandMark small/></div>}
      <div className="message-content">
        {assistant && <div className="message-label">COMMON GOODS <span>·</span> SHOPPING ASSISTANT</div>}
        <div className={`message-bubble ${assistant ? "assistant-bubble md-bubble" : "user-bubble"}`}>
          {assistant
            ? <MarkdownContent content={message.content} />
            : message.content
          }
        </div>
        {message.approvalRequired && <CheckoutApproval disabled={busy} onConfirm={() => onSend("Yes, I confirm. Please place the order.")} onCancel={() => onSend("No, cancel checkout. I do not want to place this order.")}/>}
        {assistant && message.id !== "welcome" && <div className="message-tools"><button onClick={() => navigator.clipboard?.writeText(message.content)}><Copy size={12}/> Copy</button><button onClick={() => onSend("Can you tell me more?")} disabled={busy}><Sparkles size={12}/> Ask a follow-up</button></div>}
      </div>
    </article>
  )
}
