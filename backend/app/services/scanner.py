import hashlib
import re
from typing import Dict, List

from sqlalchemy.orm import Session

from .. import models

SAMPLE_ADVISORIES = [
    {"cve": "CVE-2021-44228", "package": "log4j-core", "version": "2.14.1", "cvss": 10.0},
    {"cve": "CVE-2024-5678", "package": "lodash", "version": "4.17.20", "cvss": 5.3},
    {"cve": "MALICIOUS", "package": "event-stream", "version": "3.3.6", "cvss": 8.5},
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (RSA|EC) PRIVATE KEY-----"),
]


def severity(cvss: float) -> str:
    if cvss >= 9:
        return "CRITICAL"
    if cvss >= 7:
        return "HIGH"
    if cvss >= 4:
        return "MEDIUM"
    return "LOW"


def parse_manifest(content: str, ecosystem: str) -> List[Dict]:
    """Very small parser — accepts lines 'name==version' or JSON with deps."""
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"([\w\-.@/]+)\s*[=:]{1,2}\s*([\w.\-]+)", line)
        if m:
            deps.append({"name": m.group(1), "version": m.group(2), "ecosystem": ecosystem, "depth": 1})
    return deps


def scan_project(db: Session, project_id: str, deps: List[Dict]) -> Dict:
    findings = []
    for d in deps:
        dep = models.Dependency(project_id=project_id, **d)
        db.add(dep)
        db.flush()

        for adv in SAMPLE_ADVISORIES:
            if adv["package"] == d["name"] and adv["version"] == d["version"]:
                v = models.Vulnerability(cve=adv["cve"], package=adv["package"], version=adv["version"], cvss=adv["cvss"])
                db.add(v)
                db.flush()
                sev = severity(adv["cvss"])
                f = models.Finding(project_id=project_id, dep_id=dep.dep_id, vuln_id=v.vuln_id, severity=sev)
                db.add(f)
                findings.append({"package": d["name"], "cve": adv["cve"], "cvss": adv["cvss"], "severity": sev})

        if any(p.search(d["name"]) for p in SECRET_PATTERNS):
            f = models.Finding(project_id=project_id, dep_id=dep.dep_id, severity="HIGH", status="OPEN")
            db.add(f)
            findings.append({"package": d["name"], "issue": "SECRET_LEAK", "severity": "HIGH"})

    db.commit()
    risk = min(100, int(sum(f["cvss"] for f in findings if "cvss" in f) * 2))
    return {"risk_score": risk, "findings": findings}
