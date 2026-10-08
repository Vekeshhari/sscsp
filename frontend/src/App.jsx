import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ScanManagement from './pages/ScanManagement'
import RiskReport from './pages/RiskReport'
import AuditLog from './pages/AuditLog'

function Protected({ children, roles }) {
  const { token, role } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  if (roles && !roles.includes(role)) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Layout /></Protected>}>
        <Route index element={<Dashboard />} />
        <Route path="scan" element={<Protected roles={['developer', 'analyst', 'admin']}><ScanManagement /></Protected>} />
        <Route path="report/:projectId" element={<RiskReport />} />
        <Route path="audit" element={<Protected roles={['admin', 'auditor']}><AuditLog /></Protected>} />
      </Route>
    </Routes>
  )
}
