const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "")

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch { /* Keep the status message for non-JSON responses. */ }
    throw new Error(detail)
  }

  return response.json()
}

export const api = {
  chat: (message, conversationId) => request("/chat", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId || null }),
  }),
  cart: () => request("/cart"),
  orders: () => request("/orders?limit=20"),
}
