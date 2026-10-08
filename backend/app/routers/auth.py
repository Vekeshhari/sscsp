from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, security
from ..db import get_db
from ..services import audit

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        payload = await request.json()
        username = payload.get("username")
        password = payload.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    if not username or not password:
        audit.write(db, str(username or "unknown"), "LOGIN_FAILED", "auth")
        raise HTTPException(401, "Invalid credentials")

    user = db.query(models.User).filter_by(username=username).first()
    if not user or not security.verify_password(password, user.pw_hash):
        audit.write(db, str(username), "LOGIN_FAILED", "auth")
        raise HTTPException(401, "Invalid credentials")
    audit.write(db, user.user_id, "LOGIN_SUCCESS", "auth")
    return {"access_token": security.create_token(user.user_id, user.role), "token_type": "bearer", "role": user.role}
