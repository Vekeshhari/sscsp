import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function AuditLog() {
  const { token } = useAuth()
  const [rows, setRows] = useState([])

  useEffect(() => { api('/api/v1/audit', { token }).then(setRows).catch(() => {}) }, [])

  return (
    <div className="page">
      <h2>Audit Log</h2>
      <table className="tbl">
        <thead>
          <tr>
            <th>Time</th>
            <th>Actor</th>
            <th>Action</th>
            <th>Target</th>
            <th>Hash</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.log_id}>
              <td>{r.ts}</td>
              <td>{r.actor_id.slice(0, 8)}…</td>
              <td>{r.action}</td>
              <td>{r.target}</td>
              <td>{r.curr_hash?.slice(0, 12)}…</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
