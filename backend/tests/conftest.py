import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("EXECUTOR_USE_DOCKER", "false")
os.environ.setdefault("FORCE_INLINE_JUDGE", "true")

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.config.database import Base, SessionLocal, engine
from app.main import app
from app.models.entities import Leaderboard, Problem, TestCase, User
from app.auth.security import hash_password


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def user_token(client):
    response = client.post(
        "/signup",
        json={"name": "Ada Lovelace", "email": "ada@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture()
def admin_token(db_session, client):
    admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("strongpass123"),
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    db_session.add(Leaderboard(user_id=admin.id))
    db_session.commit()

    response = client.post("/login", json={"email": "admin@example.com", "password": "strongpass123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def sample_problem(db_session):
    problem = Problem(
        title="Add Two Numbers",
        description="Read two integers and print their sum.",
        constraints="-10^9 <= a,b <= 10^9",
        time_limit=2.0,
        memory_limit=128,
        tags="math,io",
    )
    problem.test_cases = [
        TestCase(input="2 3\n", expected_output="5\n", is_hidden=False),
        TestCase(input="10 7\n", expected_output="17\n", is_hidden=True),
    ]
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)
    return problem