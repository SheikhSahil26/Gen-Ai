import { useEffect, useRef, useState } from "react"
import { api } from "../api/client"
import { isAwaitingCheckoutApproval } from "../utils/checkout"

const welcome = {
  id: "welcome",
  role: "assistant",
  content: "Hi there. Tell me what you’re looking for and I’ll help you find it. I can also help with your cart, orders, and checkout.",
}

function readSavedChat(storageKey) {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "null")
    return saved?.messages?.length ? saved : { messages: [welcome], conversationId: null }
  } catch {
    return { messages: [welcome], conversationId: null }
  }
}

function makeId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function useChat(userId) {
  const storageKey = `common-goods-chat-v1:${userId}`
  const [saved] = useState(() => readSavedChat(storageKey))
  const [messages, setMessages] = useState(saved.messages)
  const [conversationId, setConversationId] = useState(saved.conversationId)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const scrollRef = useRef(null)

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify({ messages, conversationId }))
    const scroller = scrollRef.current
    if (scroller) scroller.scrollTo({ top: scroller.scrollHeight, behavior: "smooth" })
  }, [messages, conversationId, busy, storageKey])

  async function send(rawMessage) {
    const message = rawMessage.trim()
    if (!message || busy) return false
    const userMessage = { id: makeId(), role: "user", content: message }
    setMessages(current => [...current, userMessage])
    setError("")
    setBusy(true)

    try {
      const result = await api.chat(message, conversationId)
      setConversationId(result.conversation_id)
      setMessages(current => [...current, {
        id: makeId(),
        role: "assistant",
        content: result.message,
        intent: result.intent,
        approvalRequired: isAwaitingCheckoutApproval(result.message),
      }])
      return true
    } catch (requestError) {
      setError(requestError.message || "Could not reach the shopping assistant. Check that the backend is running.")
      return false
    } finally {
      setBusy(false)
    }
  }

  function reset() {
    const fresh = [welcome]
    setMessages(fresh)
    setConversationId(null)
    setError("")
    localStorage.removeItem(storageKey)
  }

  return { messages, conversationId, busy, error, scrollRef, send, reset, clearError: () => setError("") }
}
