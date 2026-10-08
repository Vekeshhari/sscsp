import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models


def write(db: Session, actor_id: str, action: str, target: str):
    prev = db.query(models.AuditLog).order_by(models.AuditLog.ts.desc()).first()
    prev_hash = prev.curr_hash if prev else "GENESIS"
    body = f"{actor_id}|{action}|{target}|{datetime.utcnow().isoformat()}|{prev_hash}"
    curr_hash = hashlib.sha256(body.encode()).hexdigest()
    db.add(models.AuditLog(actor_id=actor_id, action=action, target=target, prev_hash=prev_hash, curr_hash=curr_hash))
    db.commit()
