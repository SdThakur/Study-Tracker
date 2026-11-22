from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "satya", "email": "satya@example.com", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "satya"
    assert data["email"] == "satya@example.com"
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_username_fails(client: TestClient):
    payload = {"username": "dupe", "email": "dupe1@example.com", "password": "password123"}
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    payload2 = {"username": "dupe", "email": "dupe2@example.com", "password": "password123"}
    r2 = client.post("/auth/register", json=payload2)
    assert r2.status_code == 400
    assert "already registered" in r2.json()["detail"]


def test_login_and_token(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "loginuser", "email": "login@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client: TestClient):
    client.post(
        "/auth/register",
        json={"username": "wrongpw", "email": "wrongpw@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/token",
        data={"username": "wrongpw", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client: TestClient, auth_headers_user1: dict):
    response = client.get("/auth/me", headers=auth_headers_user1)
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_get_me_unauthenticated_fails(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
