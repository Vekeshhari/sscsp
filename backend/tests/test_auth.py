from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User
from app.seed import ensure_seed_users
from app.security import create_token, hash_password, verify_password


def test_password_round_trip():
    h = hash_password('Dev@12345')
    assert verify_password('Dev@12345', h)
    assert not verify_password('WrongPass', h)


def test_token_creation():
    token = create_token('user-123', 'admin')
    assert isinstance(token, str)
    assert token


def test_seed_creates_demo_users():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    created = ensure_seed_users(db)

    assert 'dev' in created
    assert 'admin' in created
    assert db.query(User).filter(User.username.in_(['dev', 'admin'])).count() == 2

    db.close()


def test_analyst_can_create_project():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    db = Session()
    user = User(user_id='u-analyst', username='analyst2', email='analyst2@x.io', role='analyst', pw_hash=hash_password('Ana@12345'))
    db.add(user)
    db.commit()

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    token = create_token(user.user_id, user.role)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        resp = client.post(
            '/api/v1/projects',
            json={'name': 'new-proj', 'repo_url': 'https://example.com/new-proj', 'criticality': 'high'},
            headers={'Authorization': f'Bearer {token}'},
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200, resp.text
    assert resp.json()['name'] == 'new-proj'

    db.close()
