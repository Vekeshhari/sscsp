from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db
from ..schemas import SignIn, VerifyIn
from ..services import audit, signer

router = APIRouter(prefix="/api/v1/artifacts", tags=["artifacts"])


@router.post("/sign")
def sign_artifact(
    body: SignIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(security.require_roles("developer", "admin")),
):
    sig = signer.sign(body.artifact_hash)
    a = models.Artifact(project_id=body.project_id, build_id=body.build_id, hash=body.artifact_hash, signature=sig, sbom_ref=body.sbom_ref)
    db.add(a)
    db.commit()
    db.refresh(a)
    audit.write(db, user.user_id, "ARTIFACT_SIGN", a.artifact_id)
    return {"artifact_id": a.artifact_id, "signature": sig}


@router.post("/verify")
def verify_artifact(body: VerifyIn, db: Session = Depends(get_db), user: models.User = Depends(security.current_user)):
    a = db.query(models.Artifact).filter_by(artifact_id=body.artifact_id).first()
    if not a:
        raise HTTPException(404, "Not found")
    ok = signer.verify(a.hash, body.signature)
    audit.write(db, user.user_id, "ARTIFACT_VERIFY", f"{a.artifact_id}:{ok}")
    return {"verified": ok, "artifact_id": a.artifact_id}
