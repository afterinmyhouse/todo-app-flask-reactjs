"""Integration tests for POST /api/v1/add-task-comment.

Uses the shared ``fake_db`` / ``auth_header`` fixtures in ``conftest.py``.
The ``FakeDb`` auto-provisions a ``tasks`` collection on attribute access,
so tests seed ownership preconditions directly via ``fake_db.tasks``.
"""

from __future__ import annotations

import pytest
from bson import ObjectId


URL = "/api/v1/add-task-comment"


def _seed_task(fake_db, *, user_oid: ObjectId) -> ObjectId:
    """Seed a task owned by ``user_oid`` and return its id."""
    return fake_db.tasks.insert({"user_id": user_oid, "title": "t", "content": "c", "status": "PENDING"})


def test_add_task_comment_success(client, fake_db, auth_header):
    user_oid = ObjectId()
    task_id = _seed_task(fake_db, user_oid=user_oid)

    response = client.post(
        URL,
        json={"taskId": str(task_id), "body": "  Looks good  "},
        headers=auth_header(user_id=str(user_oid)),
    )

    assert response.status_code == 201
    body = response.get_json()
    assert ObjectId.is_valid(body["id"])
    assert body["taskId"] == str(task_id)
    assert body["body"] == "Looks good"
    assert "createdAt" in body

    stored = fake_db.task_comments.find_one({"task_id": task_id, "user_id": user_oid})
    assert stored is not None
    assert stored["body"] == "Looks good"


def test_add_task_comment_rejects_other_users_task(client, fake_db, auth_header):
    owner_oid = ObjectId()
    task_id = _seed_task(fake_db, user_oid=owner_oid)

    # Caller is a different user; the endpoint must not leak existence.
    response = client.post(
        URL,
        json={"taskId": str(task_id), "body": "nice try"},
        headers=auth_header(user_id=str(ObjectId())),
    )

    assert response.status_code == 404
    error = response.get_json()["error"]
    assert error["code"] == "TASK_NOT_FOUND"
    assert error["details"]["resource"] == "task"


def test_add_task_comment_rejects_unknown_task(client, fake_db, auth_header):
    response = client.post(
        URL,
        json={"taskId": str(ObjectId()), "body": "nobody home"},
        headers=auth_header(),
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "TASK_NOT_FOUND"


def test_add_task_comment_rejects_invalid_task_id_format(client, auth_header):
    response = client.post(
        URL,
        json={"taskId": "not-an-objectid", "body": "hello"},
        headers=auth_header(),
    )

    assert response.status_code == 400
    error = response.get_json()["error"]
    assert error["code"] == "INVALID_TASK"
    assert error["details"]["field"] == "taskId"


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"body": "orphan"}, "taskId"),
        ({"taskId": str(ObjectId())}, "body"),
        ({}, "taskId"),
    ],
    ids=["missing_taskId", "missing_body", "missing_both"],
)
def test_add_task_comment_validation_errors(client, auth_header, payload, missing_field):
    response = client.post(URL, json=payload, headers=auth_header())

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    validation = error["details"]["validation"]["json"]
    assert missing_field in validation


def test_add_task_comment_rejects_blank_body_after_trim(client, fake_db, auth_header):
    user_oid = ObjectId()
    task_id = _seed_task(fake_db, user_oid=user_oid)

    response = client.post(
        URL,
        json={"taskId": str(task_id), "body": "     "},
        headers=auth_header(user_id=str(user_oid)),
    )

    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "body" in error["details"]["validation"]["json"]


def test_add_task_comment_requires_authentication(client):
    response = client.post(URL, json={"taskId": str(ObjectId()), "body": "hi"})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTH_REQUIRED"


def test_add_task_comment_rejects_invalid_token_subject(client, auth_header):
    response = client.post(
        URL,
        json={"taskId": str(ObjectId()), "body": "hi"},
        headers=auth_header(user_id="not-a-mongo-objectid"),
    )

    assert response.status_code == 401
    error = response.get_json()["error"]
    assert error["code"] == "INVALID_TOKEN_SUBJECT"
    assert error["details"]["field"] == "sub"
