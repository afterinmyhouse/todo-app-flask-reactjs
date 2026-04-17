from bson import ObjectId


def test_add_project_success(client, fake_db, auth_header):
    response = client.post(
        "/api/v1/add-project",
        json={"name": "Roadmap", "description": "Quarterly planning board"},
        headers=auth_header(),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert ObjectId.is_valid(body["id"])
    assert body["name"] == "Roadmap"
    assert body["description"] == "Quarterly planning board"
    assert "createdAt" in body
    assert fake_db.projects.find_one({"normalized_name": "roadmap"}) is not None


def test_add_project_rejects_duplicate_name_case_insensitive(client, fake_db, auth_header):
    headers = auth_header()
    first = client.post(
        "/api/v1/add-project",
        json={"name": "Product"},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/add-project",
        json={"name": " product "},
        headers=headers,
    )
    assert second.status_code == 409

    error = second.get_json()["error"]
    assert error["code"] == "PROJECT_EXISTS"
    assert error["details"]["field"] == "name"


def test_add_project_requires_name(client, auth_header):
    response = client.post(
        "/api/v1/add-project",
        json={"description": "Missing name"},
        headers=auth_header(),
    )

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "validation" in error["details"]


def test_add_project_requires_authentication(client):
    response = client.post("/api/v1/add-project", json={"name": "No auth"})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTH_REQUIRED"


def test_add_project_rejects_invalid_token_subject(client, auth_header):
    response = client.post(
        "/api/v1/add-project",
        json={"name": "Invalid sub"},
        headers=auth_header(user_id="not-a-mongo-objectid"),
    )

    assert response.status_code == 401
    error = response.get_json()["error"]
    assert error["code"] == "INVALID_TOKEN_SUBJECT"
    assert error["details"]["field"] == "sub"
