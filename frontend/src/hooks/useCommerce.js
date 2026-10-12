import { useCallback, useEffect, useState } from "react"
import { api } from "../api/client"

export function useCommerce() {
  const [cart, setCart] = useState(null)
  const [orders, setOrders] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const refresh = useCallback(async () => {
    setLoading(true)
    setError("")
    const [cartResult, ordersResult] = await Promise.allSettled([api.cart(), api.orders()])
    if (cartResult.status === "fulfilled") setCart(cartResult.value)
    if (ordersResult.status === "fulfilled") setOrders(ordersResult.value)
    const failures = [cartResult, ordersResult].filter(result => result.status === "rejected")
    if (failures.length) setError(failures[0].reason?.message || "Could not load your shopping details.")
    setLoading(false)
    return failures.length === 0
  }, [])

  useEffect(() => { refresh() }, [refresh])

  return { cart, orders, loading, error, refresh }
}
