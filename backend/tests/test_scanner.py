import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, SessionLocal
from app.main import app
from app.models import Dependency, Project, User
from app.security import create_token, hash_password
from app.services.scanner import parse_manifest, scan_project


def test_parse_manifest_and_scan():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    deps = parse_manifest('log4j-core==2.14.1\nlodash==4.17.20\n', 'npm')
    result = scan_project(db, 'project-1', deps)

    assert result['risk_score'] >= 0
    assert len(result['findings']) >= 2
    assert db.query(Dependency).count() >= 2

    db.close()


def test_get_scan_results_for_project():
    db = SessionLocal()
    username = f'analyst_scan_{uuid.uuid4().hex[:8]}'
    user = User(user_id=str(uuid.uuid4()), username=username, email=f'{username}@x.io', role='analyst', pw_hash=hash_password('Pass@12345'))
    project = Project(project_id=str(uuid.uuid4()), name=f'proj_{uuid.uuid4().hex[:8]}', owner_id=user.user_id, repo_url='https://example.com', criticality='high')
    db.add_all([user, project])
    db.commit()

    token = create_token(user.user_id, user.role)
    deps = parse_manifest('log4j-core==2.14.1\nlodash==4.17.20\n', 'npm')
    scan_result = scan_project(db, project.project_id, deps)
    assert scan_result['findings']

    client = TestClient(app)
    resp = client.get('/api/v1/scans', params={'project_id': project.project_id}, headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 200
    data = resp.json()
    assert data['project_id'] == project.project_id
    assert len(data['findings']) >= 2

    finding_id = data['findings'][0]['finding_id']
    assign_resp = client.post('/api/v1/scans/assign', json={'finding_id': finding_id}, headers={'Authorization': f'Bearer {token}'})
    assert assign_resp.status_code == 200
    assert assign_resp.json()['status'] == 'ASSIGNED'

    db.close()
