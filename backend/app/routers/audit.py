from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("")
def list_audit(db: Session = Depends(get_db), user: models.User = Depends(security.require_roles("admin", "auditor"))):
    return db.query(models.AuditLog).order_by(models.AuditLog.ts.desc()).limit(200).all()
