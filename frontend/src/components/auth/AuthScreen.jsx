import { useState } from "react"
import { ArrowRight, Leaf } from "lucide-react"
import { BrandMark } from "../shared/BrandMark"

export function AuthScreen({ onLogin, onRegister }) {
  const [mode, setMode] = useState("login")
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const registering = mode === "register"

  async function submit(event) {
    event.preventDefault()
    setError("")
    setBusy(true)
    try {
      if (registering) await onRegister(username.trim(), email.trim(), password)
      else await onLogin(email.trim(), password)
    } catch (submitError) {
      setError(submitError.message || "We couldn't sign you in. Please try again.")
    } finally {
      setBusy(false)
    }
  }

  return <main className="auth-page">
    <section className="auth-card" aria-labelledby="auth-title">
      <div className="auth-brand"><BrandMark/><span className="brand-name">common<span>goods</span></span></div>
      <div className="auth-leaf"><Leaf size={19}/></div>
      <p className="auth-eyebrow">YOUR THOUGHTFUL SHOPPING SPACE</p>
      <h1 id="auth-title">{registering ? "Create your account" : "Welcome back"}</h1>
      <p className="auth-description">{registering ? "Join Common Goods to get a personal shopping assistant." : "Sign in to continue to your shopping assistant."}</p>
      <form className="auth-form" onSubmit={submit}>
        {registering && <label>Username<input autoComplete="username" value={username} onChange={event => setUsername(event.target.value)} minLength={3} maxLength={100} required/></label>}
        <label>Email address<input type="email" autoComplete="email" value={email} onChange={event => setEmail(event.target.value)} maxLength={255} required/></label>
        <label>Password<input type="password" autoComplete={registering ? "new-password" : "current-password"} value={password} onChange={event => setPassword(event.target.value)} minLength={registering ? 12 : 1} maxLength={128} required/>{registering && <small>Use at least 12 characters.</small>}</label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="auth-submit" type="submit" disabled={busy}>{busy ? "Please wait…" : registering ? "Create account" : "Sign in"}<ArrowRight size={16}/></button>
      </form>
      <p className="auth-switch">{registering ? "Already have an account?" : "New to Common Goods?"} <button type="button" onClick={() => { setMode(registering ? "login" : "register"); setError("") }}>{registering ? "Sign in" : "Create an account"}</button></p>
    </section>
  </main>
}
