from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_create_and_read_study_session(client: TestClient, auth_headers_user1: dict):
    # Create course first
    c_res = client.post("/courses/", json={"title": "Python 101"}, headers=auth_headers_user1)
    course_id = c_res.json()["id"]

    # Create session
    s_res = client.post(
        "/sessions/",
        json={
            "course_id": course_id,
            "minutes": 45,
            "session_date": str(date.today()),
            "notes": "Learned FastAPI basics",
        },
        headers=auth_headers_user1,
    )
    assert s_res.status_code == 201
    session_data = s_res.json()
    assert session_data["minutes"] == 45
    assert session_data["course_id"] == course_id

    # Read session
    session_id = session_data["id"]
    get_res = client.get(f"/sessions/{session_id}", headers=auth_headers_user1)
    assert get_res.status_code == 200
    assert get_res.json()["notes"] == "Learned FastAPI basics"


def test_session_for_nonexistent_or_other_user_course_fails(
    client: TestClient, auth_headers_user1: dict, auth_headers_user2: dict
):
    # User 2 creates course
    c_res = client.post("/courses/", json={"title": "Bob's Course"}, headers=auth_headers_user2)
    course_id = c_res.json()["id"]

    # User 1 tries to log session against Bob's course -> 404
    s_res = client.post(
        "/sessions/",
        json={"course_id": course_id, "minutes": 30},
        headers=auth_headers_user1,
    )
    assert s_res.status_code == 404


def test_filter_sessions_by_course_and_date(client: TestClient, auth_headers_user1: dict):
    c1 = client.post("/courses/", json={"title": "Math"}, headers=auth_headers_user1).json()
    c2 = client.post("/courses/", json={"title": "History"}, headers=auth_headers_user1).json()

    d1 = date.today() - timedelta(days=5)
    d2 = date.today()

    client.post(
        "/sessions/",
        json={"course_id": c1["id"], "minutes": 60, "session_date": str(d1)},
        headers=auth_headers_user1,
    )
    client.post(
        "/sessions/",
        json={"course_id": c2["id"], "minutes": 40, "session_date": str(d2)},
        headers=auth_headers_user1,
    )

    # Filter by course_id
    res_c1 = client.get(f"/sessions/?course_id={c1['id']}", headers=auth_headers_user1)
    assert res_c1.status_code == 200
    assert len(res_c1.json()) == 1
    assert res_c1.json()[0]["course_id"] == c1["id"]

    # Filter by date range
    res_date = client.get(
        f"/sessions/?start_date={str(d1)}&end_date={str(d1)}",
        headers=auth_headers_user1,
    )
    assert res_date.status_code == 200
    assert len(res_date.json()) == 1


def test_update_and_delete_session(client: TestClient, auth_headers_user1: dict):
    c = client.post("/courses/", json={"title": "Science"}, headers=auth_headers_user1).json()
    s = client.post(
        "/sessions/",
        json={"course_id": c["id"], "minutes": 30, "notes": "initial"},
        headers=auth_headers_user1,
    ).json()

    # Update
    patch_res = client.patch(
        f"/sessions/{s['id']}",
        json={"minutes": 50, "notes": "extended"},
        headers=auth_headers_user1,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["minutes"] == 50
    assert patch_res.json()["notes"] == "extended"

    # Delete
    del_res = client.delete(f"/sessions/{s['id']}", headers=auth_headers_user1)
    assert del_res.status_code == 204

    # Confirm 404
    assert client.get(f"/sessions/{s['id']}", headers=auth_headers_user1).status_code == 404


def test_session_ownership_isolation(
    client: TestClient, auth_headers_user1: dict, auth_headers_user2: dict
):
    c1 = client.post("/courses/", json={"title": "Physics"}, headers=auth_headers_user1).json()
    s1 = client.post(
        "/sessions/",
        json={"course_id": c1["id"], "minutes": 25},
        headers=auth_headers_user1,
    ).json()

    # User 2 cannot access User 1's session
    assert client.get(f"/sessions/{s1['id']}", headers=auth_headers_user2).status_code == 403
    assert (
        client.patch(f"/sessions/{s1['id']}", json={"minutes": 10}, headers=auth_headers_user2).status_code
        == 403
    )
    assert client.delete(f"/sessions/{s1['id']}", headers=auth_headers_user2).status_code == 403
