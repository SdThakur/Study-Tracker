from fastapi.testclient import TestClient


def test_create_course(client: TestClient, auth_headers_user1: dict):
    response = client.post(
        "/courses/",
        json={"title": "FastAPI Mastery", "description": "From zero to hero"},
        headers=auth_headers_user1,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "FastAPI Mastery"
    assert data["description"] == "From zero to hero"
    assert "id" in data


def test_list_courses(client: TestClient, auth_headers_user1: dict):
    client.post(
        "/courses/",
        json={"title": "Course 1"},
        headers=auth_headers_user1,
    )
    client.post(
        "/courses/",
        json={"title": "Course 2"},
        headers=auth_headers_user1,
    )
    response = client.get("/courses/", headers=auth_headers_user1)
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 2


def test_get_course_by_id(client: TestClient, auth_headers_user1: dict):
    create_res = client.post(
        "/courses/",
        json={"title": "Algorithms"},
        headers=auth_headers_user1,
    )
    course_id = create_res.json()["id"]

    response = client.get(f"/courses/{course_id}", headers=auth_headers_user1)
    assert response.status_code == 200
    assert response.json()["title"] == "Algorithms"


def test_update_course(client: TestClient, auth_headers_user1: dict):
    create_res = client.post(
        "/courses/",
        json={"title": "Old Name", "description": "Old Desc"},
        headers=auth_headers_user1,
    )
    course_id = create_res.json()["id"]

    update_res = client.patch(
        f"/courses/{course_id}",
        json={"title": "New Name"},
        headers=auth_headers_user1,
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["title"] == "New Name"
    assert data["description"] == "Old Desc"


def test_delete_course(client: TestClient, auth_headers_user1: dict):
    create_res = client.post(
        "/courses/",
        json={"title": "To Delete"},
        headers=auth_headers_user1,
    )
    course_id = create_res.json()["id"]

    del_res = client.delete(f"/courses/{course_id}", headers=auth_headers_user1)
    assert del_res.status_code == 204

    get_res = client.get(f"/courses/{course_id}", headers=auth_headers_user1)
    assert get_res.status_code == 404


def test_course_not_found(client: TestClient, auth_headers_user1: dict):
    response = client.get("/courses/99999", headers=auth_headers_user1)
    assert response.status_code == 404


def test_course_ownership_isolation(
    client: TestClient, auth_headers_user1: dict, auth_headers_user2: dict
):
    # User 1 creates a course
    create_res = client.post(
        "/courses/",
        json={"title": "User 1 Private Course"},
        headers=auth_headers_user1,
    )
    course_id = create_res.json()["id"]

    # User 2 tries to read it -> 403 Forbidden
    get_res = client.get(f"/courses/{course_id}", headers=auth_headers_user2)
    assert get_res.status_code == 403

    # User 2 tries to update it -> 403 Forbidden
    patch_res = client.patch(
        f"/courses/{course_id}",
        json={"title": "Hacked Course"},
        headers=auth_headers_user2,
    )
    assert patch_res.status_code == 403

    # User 2 tries to delete it -> 403 Forbidden
    del_res = client.delete(f"/courses/{course_id}", headers=auth_headers_user2)
    assert del_res.status_code == 403

    # User 2 lists courses -> should not include User 1's course
    list_res = client.get("/courses/", headers=auth_headers_user2)
    user2_courses = list_res.json()
    assert not any(c["id"] == course_id for c in user2_courses)
