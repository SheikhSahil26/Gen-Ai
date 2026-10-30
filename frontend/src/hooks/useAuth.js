import { useCallback, useEffect, useState } from "react"
import { api, setUnauthorizedHandler } from "../api/client"

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const handleUnauthorized = useCallback(() => setUser(null), [])

  useEffect(() => {
    setUnauthorizedHandler(handleUnauthorized)
    api.authMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
    return () => setUnauthorizedHandler(null)
  }, [handleUnauthorized])

  const login = useCallback(async (email, password) => {
    const result = await api.login(email, password)
    setUser(result.user)
    return result.user
  }, [])

  const register = useCallback(async (username, email, password) => {
    const result = await api.register(username, email, password)
    setUser(result.user)
    return result.user
  }, [])

  const logout = useCallback(async () => {
    const signedInUser = user
    try {
      await api.logout()
    } finally {
      if (signedInUser?.id) localStorage.removeItem(`common-goods-chat-v1:${signedInUser.id}`)
      setUser(null)
    }
  }, [user])

  return { user, loading, login, register, logout }
}
