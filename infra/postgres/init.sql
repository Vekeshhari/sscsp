CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL,
  pw_hash TEXT NOT NULL,
  mfa BOOLEAN DEFAULT FALSE,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  owner_id TEXT NOT NULL,
  repo_url TEXT NOT NULL,
  criticality TEXT DEFAULT 'medium',
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dependencies (
  dep_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  ecosystem TEXT NOT NULL,
  hash TEXT,
  depth INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
  vuln_id TEXT PRIMARY KEY,
  cve TEXT NOT NULL,
  package TEXT NOT NULL,
  version TEXT NOT NULL,
  cvss DOUBLE PRECISION NOT NULL,
  source TEXT DEFAULT 'OSV'
);

CREATE TABLE IF NOT EXISTS findings (
  finding_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  dep_id TEXT NOT NULL,
  vuln_id TEXT,
  severity TEXT NOT NULL,
  status TEXT DEFAULT 'OPEN',
  detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  build_id TEXT NOT NULL,
  hash TEXT NOT NULL,
  signature TEXT NOT NULL,
  sbom_ref TEXT,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS remediations (
  rem_id TEXT PRIMARY KEY,
  finding_id TEXT NOT NULL,
  action TEXT NOT NULL,
  assignee TEXT NOT NULL,
  status TEXT DEFAULT 'OPEN',
  due TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
  log_id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  prev_hash TEXT,
  curr_hash TEXT NOT NULL
);
