from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, SessionLocal, engine
from .routers import artifacts, audit, auth, projects, scans
from .seed import ensure_seed_users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SSCSP API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    seeded = ensure_seed_users(db)
    if seeded:
        print(f"Seeded users: {' / '.join(seeded)}")
    db.close()


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(scans.router)
app.include_router(artifacts.router)
app.include_router(audit.router)


@app.get("/health")
def health():
    return {"status": "ok"}
