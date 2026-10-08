import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import SeverityBadge from '../components/SeverityBadge'

export default function ScanManagement() {
  const { token } = useAuth()
  const [projects, setProjects] = useState([])
  const [selected, setSelected] = useState(null)
  const [findings, setFindings] = useState([])

  useEffect(() => { api('/api/v1/projects', { token }).then(setProjects) }, [])

  async function loadFindings(pid) {
    setSelected(pid)
    const r = await api(`/api/v1/scans?project_id=${pid}`, { token }).catch(() => ({ findings: [] }))
    setFindings(r.findings || [])
  }

  async function assignFinding(finding) {
    await api('/api/v1/scans/assign', {
      method: 'POST',
      token,
      body: { finding_id: finding.finding_id },
    })
    setFindings((current) => current.map((item) => item.finding_id === finding.finding_id ? { ...item, status: 'ASSIGNED' } : item))
  }

  return (
    <div className="page">
      <h2>Security Analyst · Scan Management</h2>
      <div className="split">
        <div className="queue card">
          <h3>Projects</h3>
          {projects.map((p) => (
            <div key={p.project_id} className={p.project_id === selected ? 'row active' : 'row'} onClick={() => loadFindings(p.project_id)}>
              {p.name}
            </div>
          ))}
        </div>
        <div className="detail card">
          <h3>Findings</h3>
          {findings.length === 0 && <p>No findings loaded. Select a project.</p>}
          <table className="tbl">
            <thead>
              <tr>
                <th>Package</th>
                <th>CVE</th>
                <th>Severity</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {findings.map((f, i) => (
                <tr key={i}>
                  <td>{f.package}</td>
                  <td>{f.cve}</td>
                  <td><SeverityBadge level={f.severity} /></td>
                  <td>
                    {f.status === 'ASSIGNED' ? <button disabled>Assigned</button> : <button onClick={() => assignFinding(f)}>Assign</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
