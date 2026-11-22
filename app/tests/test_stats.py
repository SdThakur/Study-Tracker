from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_empty_stats(client: TestClient, auth_headers_user1: dict):
    response = client.get("/stats/", headers=auth_headers_user1)
    assert response.status_code == 200
    data = response.json()
    assert data["total_minutes"] == 0
    assert data["total_sessions"] == 0
    assert data["weekly_streak"] == 0
    assert data["courses"] == []


def test_stats_aggregation_and_weekly_streak(client: TestClient, auth_headers_user1: dict):
    # Create two courses
    c1 = client.post("/courses/", json={"title": "Data Structures"}, headers=auth_headers_user1).json()
    c2 = client.post("/courses/", json={"title": "Computer Networks"}, headers=auth_headers_user1).json()

    # Log sessions in current week
    today = date.today()
    client.post(
        "/sessions/",
        json={"course_id": c1["id"], "minutes": 60, "session_date": str(today)},
        headers=auth_headers_user1,
    )
    client.post(
        "/sessions/",
        json={"course_id": c1["id"], "minutes": 30, "session_date": str(today)},
        headers=auth_headers_user1,
    )
    client.post(
        "/sessions/",
        json={"course_id": c2["id"], "minutes": 45, "session_date": str(today)},
        headers=auth_headers_user1,
    )

    # Log a session in previous week (7 days ago) to test weekly streak
    last_week_date = today - timedelta(days=7)
    client.post(
        "/sessions/",
        json={"course_id": c2["id"], "minutes": 50, "session_date": str(last_week_date)},
        headers=auth_headers_user1,
    )

    stats_res = client.get("/stats/", headers=auth_headers_user1)
    assert stats_res.status_code == 200
    stats = stats_res.json()

    assert stats["total_minutes"] == 60 + 30 + 45 + 50  # 185
    assert stats["total_sessions"] == 4
    assert stats["weekly_streak"] >= 2

    # Check course breakdown
    course_map = {c["course_title"]: c for c in stats["courses"]}
    assert course_map["Data Structures"]["total_minutes"] == 90
    assert course_map["Data Structures"]["session_count"] == 2
    assert course_map["Computer Networks"]["total_minutes"] == 95
    assert course_map["Computer Networks"]["session_count"] == 2
