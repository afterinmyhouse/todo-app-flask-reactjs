"""Tests for GET /api/v1/tasks/user serialization and ownership scoping."""

from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId

URL = "/api/v1/tasks/user"


def _seed_task(fake_db, *, user_oid: ObjectId, title: str, tag_name: str | None, **extra):
    doc = {
        "user_id": user_oid,
        "title": title,
        "content": extra.get("content", "body"),
        "status": extra.get("status", "PENDING"),
        "created_at": extra.get("created_at", datetime.now(timezone.utc)),
        "tag_name": tag_name,
    }
    return fake_db.tasks.insert(doc)


def test_list_includes_tag_name_and_created_at(client, fake_db, auth_header):
    user_oid = ObjectId()
    created = datetime(2026, 4, 9, 12, 0, tzinfo=timezone.utc)
    task_id = _seed_task(
        fake_db,
        user_oid=user_oid,
        title="Team meeting",
        tag_name="Work",
        created_at=created,
    )

    response = client.get(URL, headers=auth_header(user_id=str(user_oid)))

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == str(task_id)
    assert body[0]["title"] == "Team meeting"
    assert body[0]["tagName"] == "Work"
    assert body[0]["createdAt"] == "2026-04-09T12:00:00+00:00"


def test_list_allows_untagged_project_tasks(client, fake_db, auth_header):
    user_oid = ObjectId()
    _seed_task(fake_db, user_oid=user_oid, title="No tag", tag_name=None)

    response = client.get(URL, headers=auth_header(user_id=str(user_oid)))

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["tagName"] is None
    assert "createdAt" in body[0]


def test_list_does_not_return_other_users_tasks(client, fake_db, auth_header):
    owner = ObjectId()
    other = ObjectId()
    _seed_task(fake_db, user_oid=other, title="Secret", tag_name="Private")

    response = client.get(URL, headers=auth_header(user_id=str(owner)))

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_requires_auth(client):
    response = client.get(URL)
    assert response.status_code == 401
