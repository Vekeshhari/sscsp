"""End-to-end validation test: register → scan → sign → verify."""
import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_e2e_register_scan_sign_verify():
    token = client.post(
        "/api/v1/auth/login",
        json={"username": "dev", "password": "Dev@12345"},
    ).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    project_name = f"e2e-demo-{uuid.uuid4().hex[:8]}"
    pid = client.post(
        "/api/v1/projects",
        headers=h,
        json={"name": project_name, "repo_url": f"https://x.io/{project_name}", "criticality": "high"},
    ).json()["project_id"]

    scan = client.post(
        "/api/v1/scans",
        headers=h,
        json={"project_id": pid, "ecosystem": "npm", "manifest": "log4j-core==2.14.1"},
    ).json()
    assert scan["risk_score"] > 0

    signed = client.post(
        "/api/v1/artifacts/sign",
        headers=h,
        json={"project_id": pid, "build_id": "build-001", "artifact_hash": "sha256:abc123", "sbom_ref": "sbom-001.json"},
    ).json()
    assert "signature" in signed

    verified = client.post(
        "/api/v1/artifacts/verify",
        headers=h,
        json={"artifact_id": signed["artifact_id"], "signature": signed["signature"]},
    ).json()
    assert verified["verified"] is True
