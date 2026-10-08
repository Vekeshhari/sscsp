import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Layout() {
  const { role, logout } = useAuth()
  const nav = useNavigate()

  return (
    <div className="app">
      <header className="hdr">
        <b>🔒 SSCSP</b>
        <span>role: {role}</span>
        <button onClick={() => { logout(); nav('/login') }}>Logout</button>
      </header>
      <aside className="nav">
        <NavLink to="/">Dashboard</NavLink>
        {['developer', 'analyst', 'admin'].includes(role) && <NavLink to="/scan">Scan Management</NavLink>}
        {['admin', 'auditor'].includes(role) && <NavLink to="/audit">Audit Log</NavLink>}
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  )
}
