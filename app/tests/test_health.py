from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "X-Process-Time" in response.headers


def test_root_browser_html_request(client: TestClient):
    response = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Study Tracker" in response.text


def test_frontend_app_endpoint(client: TestClient):
    response = client.get("/app")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Study Tracker" in response.text


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
