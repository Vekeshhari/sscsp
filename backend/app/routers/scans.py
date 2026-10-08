from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db
from ..schemas import ScanIn
from ..services import audit, scanner

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


@router.get("")
def list_findings(project_id: str, db: Session = Depends(get_db), user: models.User = Depends(security.current_user)):
    project = db.query(models.Project).filter_by(project_id=project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if user.role == "developer" and project.owner_id != user.user_id:
        raise HTTPException(403, "Not your project")

    rows = []
    findings = (
        db.query(models.Finding)
        .filter(models.Finding.project_id == project_id)
        .order_by(models.Finding.detected.desc())
        .all()
    )
    for finding in findings:
        dep = db.query(models.Dependency).filter_by(dep_id=finding.dep_id).first()
        vuln = db.query(models.Vulnerability).filter_by(vuln_id=finding.vuln_id).first() if finding.vuln_id else None
        rows.append({
            "finding_id": finding.finding_id,
            "package": dep.name if dep else "unknown",
            "cve": vuln.cve if vuln else None,
            "severity": finding.severity,
            "status": finding.status,
        })
    return {"project_id": project_id, "findings": rows}


@router.post("/assign")
def assign_finding(
    body: dict,
    db: Session = Depends(get_db),
    user: models.User = Depends(security.require_roles("analyst", "admin")),
):
    finding_id = body.get("finding_id")
    if not finding_id:
        raise HTTPException(400, "finding_id is required")

    finding = db.query(models.Finding).filter_by(finding_id=finding_id).first()
    if not finding:
        raise HTTPException(404, "Finding not found")

    finding.status = "ASSIGNED"
    rem = models.Remediation(
        finding_id=finding.finding_id,
        action="Investigate and remediate",
        assignee=user.user_id,
        status="OPEN",
    )
    db.add(rem)
    db.commit()
    db.refresh(rem)
    audit.write(db, user.user_id, "FINDING_ASSIGN", finding.finding_id)
    return {"finding_id": finding.finding_id, "status": finding.status, "assignee": user.user_id, "remediation_id": rem.rem_id}


@router.post("")
def run_scan(body: ScanIn, db: Session = Depends(get_db), user: models.User = Depends(security.current_user)):
    project = db.query(models.Project).filter_by(project_id=body.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    if user.role == "developer" and project.owner_id != user.user_id:
        raise HTTPException(403, "Not your project")

    deps = scanner.parse_manifest(body.manifest, body.ecosystem)
    result = scanner.scan_project(db, project.project_id, deps)
    audit.write(db, user.user_id, "SCAN_RUN", project.project_id)
    return result
