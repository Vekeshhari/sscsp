export default function SeverityBadge({ level }) {
  const colors = { CRITICAL: '#b00020', HIGH: '#e65100', MEDIUM: '#f9a825', LOW: '#2e7d32' }
  return <span className="badge" style={{ background: colors[level] || '#555' }}>{level}</span>
}
