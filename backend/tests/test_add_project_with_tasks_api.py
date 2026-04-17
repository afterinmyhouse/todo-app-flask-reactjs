"""Integration tests for POST /api/v1/add-project-with-tasks.

Covers success, every documented 4xx failure mode, and the
compensation-on-partial-failure path (5xx).
"""

from __future__ import annotations

import pytest
from bson import ObjectId


URL = "/api/v1/add-project-with-tasks"


def _seed_tag(fake_db, *, name: str = "Work") -> ObjectId:
    return fake_db.tags.insert({"name": name})


def _valid_payload(**overrides):
    payload = {
        "name": "Launch",
        "description": "Initial plan",
        "tasks": [
            {"title": "Write spec"},
            {"title": "Draft UI", "status": "IN_PROGRESS"},
        ],
    }
    payload.update(overrides)
    return payload


def test_creates_project_and_tasks(client, fake_db, auth_header):
    user_oid = ObjectId()

    response = client.post(URL, json=_valid_payload(), headers=auth_header(user_id=str(user_oid)))

    assert response.status_code == 201
    body = response.get_json()
    assert ObjectId.is_valid(body["id"])
    assert body["name"] == "Launch"
    assert body["description"] == "Initial plan"
    assert "createdAt" in body
    assert len(body["tasks"]) == 2

    titles = [t["title"] for t in body["tasks"]]
    assert titles == ["Write spec", "Draft UI"]
    assert body["tasks"][0]["status"] == "PENDING"
    assert body["tasks"][1]["status"] == "IN_PROGRESS"
    assert all("tagName" in t for t in body["tasks"])
    assert all(t["tagName"] is None for t in body["tasks"])

    # Persisted state matches the response and carries the ownership link.
    stored_project = fake_db.projects.find_one({"user_id": user_oid})
    assert stored_project is not None
    assert stored_project["normalized_name"] == "launch"
    project_id = stored_project["_id"]
    assert len(fake_db.tasks.docs) == 2
    assert all(doc["project_id"] == project_id for doc in fake_db.tasks.docs)
    assert all(doc["user_id"] == user_oid for doc in fake_db.tasks.docs)


def test_resolves_tag_name_for_tasks_with_tag(client, fake_db, auth_header):
    user_oid = ObjectId()
    tag_id = _seed_tag(fake_db, name="Work")

    payload = _valid_payload(
        tasks=[
            {"title": "With tag", "tagId": str(tag_id)},
            {"title": "Without tag"},
        ]
    )
    response = client.post(URL, json=payload, headers=auth_header(user_id=str(user_oid)))

    assert response.status_code == 201
    tasks = response.get_json()["tasks"]
    assert tasks[0]["tagName"] == "Work"
    assert tasks[1]["tagName"] is None


def test_rejects_duplicate_project_name_for_user(client, fake_db, auth_header):
    user_oid = ObjectId()
    headers = auth_header(user_id=str(user_oid))

    first = client.post(URL, json=_valid_payload(name="Alpha"), headers=headers)
    assert first.status_code == 201

    second = client.post(
        URL,
        json=_valid_payload(name=" alpha "),
        headers=headers,
    )
    assert second.status_code == 409
    error = second.get_json()["error"]
    assert error["code"] == "PROJECT_EXISTS"
    assert error["details"]["field"] == "name"

    # No extra tasks should have been written on the failed second request.
    assert len(fake_db.tasks.docs) == 2


def test_rejects_duplicate_task_titles_in_request(client, fake_db, auth_header):
    payload = _valid_payload(
        tasks=[
            {"title": "Same"},
            {"title": " same "},
        ]
    )
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "DUPLICATE_TASK_TITLE"
    assert error["details"]["field"] == "tasks[1].title"
    # No side effects on duplicate-title pre-validation failure.
    assert fake_db.projects.find_one({}) is None
    assert fake_db.tasks.find_one({}) is None


def test_rejects_invalid_tag_id_format(client, fake_db, auth_header):
    payload = _valid_payload(
        tasks=[{"title": "Bad tag", "tagId": "not-an-objectid"}]
    )
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 400
    error = response.get_json()["error"]
    assert error["code"] == "INVALID_TAG"
    assert error["details"]["field"] == "tasks[0].tagId"
    assert fake_db.projects.find_one({}) is None


def test_rejects_unknown_tag(client, fake_db, auth_header):
    payload = _valid_payload(
        tasks=[{"title": "Missing tag", "tagId": str(ObjectId())}]
    )
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 404
    error = response.get_json()["error"]
    assert error["code"] == "TAG_NOT_FOUND"
    assert error["details"]["resource"] == "tag"
    assert fake_db.projects.find_one({}) is None


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"description": "x", "tasks": [{"title": "t"}]}, "name"),
        ({"name": "n", "description": "x"}, "tasks"),
        ({"name": "n", "tasks": []}, "tasks"),
    ],
    ids=["missing_name", "missing_tasks", "empty_tasks"],
)
def test_validation_errors_for_top_level_shape(client, auth_header, payload, missing_field):
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert missing_field in error["details"]["validation"]["json"]


def test_validation_error_when_task_missing_title(client, auth_header):
    payload = _valid_payload(tasks=[{"status": "PENDING"}])
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    task_errors = error["details"]["validation"]["json"]["tasks"]
    # Marshmallow reports index-keyed errors for list-of-nested fields.
    assert "0" in task_errors
    assert "title" in task_errors["0"]


def test_validation_error_when_too_many_tasks(client, auth_header):
    payload = _valid_payload(tasks=[{"title": f"task-{i}"} for i in range(51)])
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "tasks" in error["details"]["validation"]["json"]


def test_blank_task_title_after_trim_is_rejected(client, fake_db, auth_header):
    payload = _valid_payload(tasks=[{"title": "   "}])
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "tasks[0].title" in error["details"]["validation"]["json"]
    assert fake_db.projects.find_one({}) is None


def test_requires_authentication(client):
    response = client.post(URL, json=_valid_payload())
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTH_REQUIRED"


def test_rejects_invalid_token_subject(client, auth_header):
    response = client.post(URL, json=_valid_payload(), headers=auth_header(user_id="bad"))
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "INVALID_TOKEN_SUBJECT"


def test_compensation_rolls_back_project_when_task_insert_fails(client, fake_db, auth_header, app):
    """Simulate a mid-flight DB failure and assert the project is rolled back.

    We wrap ``fake_db.tasks.insert_one`` so the second call raises. The
    controller should delete the project (and any tasks already written)
    so the caller never observes a half-applied state.
    """
    original_insert = fake_db.tasks.insert_one
    calls = {"n": 0}

    def flaky_insert(doc):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated mongo failure")
        return original_insert(doc)

    fake_db.tasks.insert_one = flaky_insert

    payload = _valid_payload(
        tasks=[
            {"title": "Will land"},
            {"title": "Will fail"},
        ]
    )
    # Disable Flask propagation so test_client returns a 500 instead of raising.
    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        response = client.post(URL, json=payload, headers=auth_header())
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = None

    assert response.status_code == 500

    # Compensation: the project and every task inserted before the failure
    # must have been removed, so the collections look as if nothing happened.
    assert fake_db.projects.find_one({}) is None, fake_db.projects.docs
    assert fake_db.tasks.find_one({}) is None, fake_db.tasks.docs
