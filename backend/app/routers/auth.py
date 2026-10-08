from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db
from ..services import audit

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=form.username).first()
    if not user or not security.verify_password(form.password, user.pw_hash):
        audit.write(db, form.username, "LOGIN_FAILED", "auth")
        raise HTTPException(401, "Invalid credentials")
    audit.write(db, user.user_id, "LOGIN_SUCCESS", "auth")
    return {"access_token": security.create_token(user.user_id, user.role), "token_type": "bearer", "role": user.role}
