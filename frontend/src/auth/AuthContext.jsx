import { createContext, useContext, useState } from 'react'
import { api } from '../api/client'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(sessionStorage.getItem('token'))
  const [role, setRole] = useState(sessionStorage.getItem('role'))

  async function login(username, password) {
    const form = new URLSearchParams({ username, password })
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    })
    if (!res.ok) throw new Error('Invalid credentials')
    const data = await res.json()
    setToken(data.access_token)
    setRole(data.role)
    sessionStorage.setItem('token', data.access_token)
    sessionStorage.setItem('role', data.role)
  }

  function logout() {
    setToken(null)
    setRole(null)
    sessionStorage.clear()
  }

  return (
    <AuthCtx.Provider value={{ token, role, login, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}
