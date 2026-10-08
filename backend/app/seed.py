from sqlalchemy.orm import Session

from . import models
from .db import Base, SessionLocal, engine
from .security import hash_password

DEFAULT_USERS = [
    ("dev", "dev@x.io", "developer", "Dev@12345"),
    ("dev1", "dev1@x.io", "developer", "Dev1@12345"),
    ("analyst", "analyst@x.io", "analyst", "Ana@12345"),
    ("admin", "admin@x.io", "admin", "Adm@12345"),
    ("auditor", "auditor@x.io", "auditor", "Aud@12345"),
]


def ensure_seed_users(db: Session):
    created = []
    for username, email, role, password in DEFAULT_USERS:
        if not db.query(models.User).filter_by(username=username).first():
            db.add(models.User(username=username, email=email, role=role, pw_hash=hash_password(password)))
            created.append(username)
    if created:
        db.commit()
    return created


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seeded = ensure_seed_users(db)
    if seeded:
        print(f"Seeded users: {' / '.join(seeded)}")
    else:
        print("Already seeded")
    db.close()
