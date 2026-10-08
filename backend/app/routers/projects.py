from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db
from ..schemas import ProjectIn, ProjectOut
from ..services import audit

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectOut)
def create_project(
    body: ProjectIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(security.require_roles("developer", "analyst", "admin", "auditor")),
):
    p = models.Project(name=body.name, owner_id=user.user_id, repo_url=body.repo_url, criticality=body.criticality)
    db.add(p)
    db.commit()
    db.refresh(p)
    audit.write(db, user.user_id, "PROJECT_CREATE", p.project_id)
    return p


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: models.User = Depends(security.current_user)):
    q = db.query(models.Project)
    if user.role == "developer":
        q = q.filter_by(owner_id=user.user_id)
    return q.all()
