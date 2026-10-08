import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import SeverityBadge from '../components/SeverityBadge'

export default function RiskReport() {
  const { projectId } = useParams()
  const { token } = useAuth()
  const [data, setData] = useState(null)

  function getSbomJson() {
    if (!data) return ''
    const sbom = {
      bomFormat: 'CycloneDX',
      specVersion: '1.5',
      version: 1,
      metadata: {
        timestamp: new Date().toISOString(),
        component: {
          type: 'application',
          name: data.project?.name || 'Project',
        },
      },
      components: data.findings.map((f) => ({
        type: 'library',
        name: f.package,
        version: 'unknown',
        purl: `pkg:npm/${f.package}`,
        properties: [{ name: 'CVE', value: f.cve || 'N/A' }],
      })),
    }
    return JSON.stringify(sbom, null, 2)
  }

  function exportPdf() {
    if (!data) return

    const rows = data.findings.map((f) => `
      <tr>
        <td>${f.package}</td>
        <td>${f.cve}</td>
        <td>${f.severity}</td>
        <td>${f.status}</td>
      </tr>
    `).join('')

    const printWindow = window.open('', '_blank', 'width=900,height=700')
    if (!printWindow) {
      window.alert('Please allow popups to export the PDF report.')
      return
    }

    printWindow.document.write(`
      <html>
        <head>
          <title>Risk Report - ${data.project?.name || 'Project'}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 24px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
          </style>
        </head>
        <body>
          <h1>Risk Report</h1>
          <p><strong>Project:</strong> ${data.project?.name || 'N/A'}</p>
          <p><strong>Risk Score:</strong> ${data.risk}</p>
          <table>
            <thead>
              <tr><th>Package</th><th>CVE</th><th>Severity</th><th>Status</th></tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.focus()
    setTimeout(() => printWindow.print(), 300)
  }

  useEffect(() => {
    api('/api/v1/projects', { token }).then((list) => {
      const p = list.find((x) => x.project_id === projectId)
      setData({
        project: p,
        risk: 87,
        findings: [
          { package: 'log4j-core', cve: 'CVE-2021-44228', cvss: 10.0, severity: 'CRITICAL', status: 'OPEN' },
          { package: 'event-stream', cve: 'MALICIOUS', cvss: 8.5, severity: 'HIGH', status: 'OPEN' },
          { package: 'lodash', cve: 'CVE-2024-5678', cvss: 5.3, severity: 'MEDIUM', status: 'IN PROGRESS' },
        ],
      })
    })
  }, [projectId, token])

  if (!data) return <p>Loading…</p>

  return (
    <div className="page">
      <h2>Risk Report · {data.project?.name}</h2>
      <div className="cards">
        <div className="card score">Risk {data.risk}</div>
        <div className="card">Critical: 1</div>
        <div className="card">High: 1</div>
        <div className="card">Medium: 1</div>
      </div>
      <div className="card">
        <h3>Findings</h3>
        <table className="tbl">
          <thead>
            <tr>
              <th>Package</th>
              <th>CVE</th>
              <th>CVSS</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.findings.map((f, i) => (
              <tr key={i}>
                <td>{f.package}</td>
                <td>{f.cve}</td>
                <td>{f.cvss}</td>
                <td><SeverityBadge level={f.severity} /></td>
                <td>{f.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h3>SBOM (CycloneDX preview)</h3>
        <pre>{JSON.stringify({ components: data.findings.map((f) => f.package) }, null, 2)}</pre>
        <a
          href={`data:application/json;charset=utf-8,${encodeURIComponent(getSbomJson())}`}
          download={`${(data.project?.name || 'project').replace(/\s+/g, '-').toLowerCase()}-sbom.json`}
          style={{ display: 'inline-block', marginRight: 12, padding: '10px 16px', background: '#1e88e5', color: 'white', borderRadius: 6, textDecoration: 'none' }}
        >
          Export SBOM
        </a>
        <a
          href="#"
          onClick={(e) => { e.preventDefault(); exportPdf(); }}
          style={{ display: 'inline-block', padding: '10px 16px', background: '#1e88e5', color: 'white', borderRadius: 6, textDecoration: 'none' }}
        >
          Export PDF
        </a>
      </div>
    </div>
  )
}
