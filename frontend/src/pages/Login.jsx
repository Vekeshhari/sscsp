import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { login } = useAuth()
  const nav = useNavigate()

  const valid = username.length >= 3 && password.length >= 8

  async function submit(e) {
    e.preventDefault()
    if (!valid) return
    setBusy(true)
    setError('')
    try {
      await login(username, password)
      nav('/')
    } catch (err) {
      setError('Invalid credentials. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit} autoComplete="off">
        <h1>🔒 SSCSP</h1>
        <p className="sub">Software Supply Chain Security Platform</p>

        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />

        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

        <label>MFA Code (demo: skip)</label>
        <input inputMode="numeric" maxLength={6} placeholder="000000" />

        <button disabled={!valid || busy}>{busy ? 'Signing in…' : 'Sign In with SSO'}</button>

        {error && <div className="err">⚠ {error}</div>}
        <div className="hint">Forgot password? · Contact Admin</div>
      </form>
    </div>
  )
}
