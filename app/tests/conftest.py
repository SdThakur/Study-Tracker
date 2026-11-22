import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine
from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    # Use isolated in-memory SQLite database for testing (Lesson 9)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Override get_session dependency with our in-memory test session
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers_user1")
def auth_headers_user1_fixture(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    res = client.post(
        "/auth/token",
        data={"username": "alice", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="auth_headers_user2")
def auth_headers_user2_fixture(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "password456"},
    )
    res = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password456"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
