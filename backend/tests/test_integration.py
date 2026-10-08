"""Integration test: API + DB + auth flow."""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.db import Base, get_db
from app.main import app
from app.security import hash_password

DB_PATH = f"sqlite:///./test_integration_{uuid.uuid4().hex}.db"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSession()
    db.add(
        models.User(
            username="dev",
            email="dev@x.io",
            role="developer",
            pw_hash=hash_password("Dev@12345"),
        )
    )
    db.commit()
    db.close()
    yield


def _token():
    r = client.post("/api/v1/auth/login", json={"username": "dev", "password": "Dev@12345"})
    return r.json()["access_token"]


def test_full_project_scan_flow():
    """Login → create project → scan manifest → read findings."""
    token = _token()
    headers = {"Authorization": f"Bearer {token}"}

    project_name = f"int-test-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": project_name, "repo_url": f"https://x.io/{project_name}", "criticality": "high"},
    )
    assert r.status_code == 200
    pid = r.json()["project_id"]

    r = client.post(
        "/api/v1/scans",
        headers=headers,
        json={"project_id": pid, "ecosystem": "npm", "manifest": "log4j-core==2.14.1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["risk_score"] > 0
    assert any(f["cve"] == "CVE-2021-44228" for f in body["findings"])


def test_project_isolation_between_users():
    """User A cannot see User B's projects."""
    token = _token()
    headers = {"Authorization": f"Bearer {token}"}
    other_name = f"int-test-2-{uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": other_name, "repo_url": f"https://x.io/{other_name}", "criticality": "low"},
    )

    r = client.get("/api/v1/projects")
    assert r.status_code == 401
