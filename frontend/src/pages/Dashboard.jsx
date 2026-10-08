import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function Dashboard() {
  const { token, role } = useAuth()
  const [projects, setProjects] = useState([])
  const [manifest, setManifest] = useState('log4j-core==2.14.1\nlodash==4.17.20')
  const [ecosystem, setEco] = useState('npm')
  const [name, setName] = useState('')
  const [msg, setMsg] = useState('')
  const canCreateProject = ['developer', 'analyst', 'admin', 'auditor'].includes(role)
  const canRunScan = ['developer', 'analyst', 'admin'].includes(role)

  async function load() {
    const list = await api('/api/v1/projects', { token })
    setProjects(list)
  }

  useEffect(() => { load() }, [])

  async function createProject(e) {
    e.preventDefault()
    if (name.length < 2) return
    await api('/api/v1/projects', {
      method: 'POST',
      token,
      body: { name, repo_url: `https://github.com/x/${name}`, criticality: 'high' },
    })
    setName('')
    load()
  }

  async function runScan(pid) {
    const r = await api('/api/v1/scans', {
      method: 'POST',
      token,
      body: { project_id: pid, ecosystem, manifest },
    })
    setMsg(`Scan done · risk ${r.risk_score} · ${r.findings.length} findings`)
  }

  return (
    <div className="page">
      <h2>My Projects</h2>

      {canCreateProject && (
        <form className="card" onSubmit={createProject}>
          <input placeholder="New project name" value={name} onChange={(e) => setName(e.target.value)} />
          <button disabled={name.length < 2}>+ Register Project</button>
        </form>
      )}

      {canRunScan && (
        <div className="card">
          <h3>Run a scan</h3>
          <select value={ecosystem} onChange={(e) => setEco(e.target.value)}>
            <option>npm</option>
            <option>pypi</option>
            <option>maven</option>
          </select>
          <textarea rows={4} value={manifest} onChange={(e) => setManifest(e.target.value)} />
        </div>
      )}

      <table className="tbl">
        <thead>
          <tr>
            <th>Project</th>
            <th>Criticality</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.project_id}>
              <td>{p.name}</td>
              <td>{p.criticality}</td>
              <td>
                {canRunScan && <button onClick={() => runScan(p.project_id)}>Scan Now</button>}
                <Link to={`/report/${p.project_id}`}><button>Report</button></Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {msg && <div className="ok">{msg}</div>}
    </div>
  )
}
