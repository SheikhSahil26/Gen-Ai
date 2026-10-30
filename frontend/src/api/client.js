const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "")
let unauthorizedHandler = null

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
  })

  if (!response.ok) {
    if (response.status === 401) unauthorizedHandler?.()
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      detail = Array.isArray(body.detail)
        ? body.detail.map(issue => issue.msg).join(" ")
        : body.detail || detail
    } catch { /* Keep the status message for non-JSON responses. */ }
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  if (response.status === 204) return null
  return response.json()
}

export const api = {
  authMe: () => request("/auth/me"),
  login: (email, password) => request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }),
  register: (username, email, password) => request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  }),
  logout: () => request("/auth/logout", { method: "POST" }),
  chat: (message, conversationId) => request("/chat", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId || null }),
  }),
  cart: () => request("/cart"),
  orders: () => request("/orders?limit=20"),
}
