"""Tests for GET /api/v1/search (JWT-scoped workspace search)."""

from __future__ import annotations

import pytest
from bson import ObjectId

URL = "/api/v1/search"


def test_search_returns_tasks_tags_projects(client, fake_db, auth_header):
    user_oid = ObjectId()
    headers = auth_header(user_id=str(user_oid))

    fake_db.tags.insert({"name": "Meeting notes"})
    fake_db.tasks.insert(
        {
            "user_id": user_oid,
            "title": "Team meeting prep",
            "content": "Agenda items for Monday sync.",
            "status": "PENDING",
            "tag_name": "Meeting notes",
        }
    )
    fake_db.projects.insert(
        {
            "user_id": user_oid,
            "name": "Roadmap meeting",
            "description": "Q2 planning",
            "normalized_name": "roadmap meeting",
        }
    )

    response = client.get(URL, query_string={"q": "meet"}, headers=headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"] == "meet"
    assert len(body["results"]["tags"]) == 1
    assert body["results"]["tags"][0]["name"] == "Meeting notes"
    assert len(body["results"]["tasks"]) == 1
    assert body["results"]["tasks"][0]["title"] == "Team meeting prep"
    assert body["results"]["tasks"][0]["tagName"] == "Meeting notes"
    assert "snippet" in body["results"]["tasks"][0]
    assert len(body["results"]["projects"]) == 1
    assert body["results"]["projects"][0]["name"] == "Roadmap meeting"


def test_search_does_not_return_other_users_tasks(client, fake_db, auth_header):
    owner = ObjectId()
    other = ObjectId()
    fake_db.tasks.insert(
        {
            "user_id": other,
            "title": "Secret meeting",
            "content": "private",
            "status": "PENDING",
            "tag_name": None,
        }
    )

    response = client.get(
        URL,
        query_string={"q": "meeting"},
        headers=auth_header(user_id=str(owner)),
    )

    assert response.status_code == 200
    assert response.get_json()["results"]["tasks"] == []


def test_search_short_query_returns_empty_buckets(client, auth_header):
    response = client.get(URL, query_string={"q": "x"}, headers=auth_header())
    assert response.status_code == 200
    body = response.get_json()
    assert body["results"]["tags"] == []
    assert body["results"]["tasks"] == []
    assert body["results"]["projects"] == []


def test_search_query_too_long(client, auth_header):
    response = client.get(
        URL,
        query_string={"q": "a" * 121},
        headers=auth_header(),
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "BAD_REQUEST"


def test_search_requires_auth(client):
    response = client.get(URL, query_string={"q": "test"})
    assert response.status_code == 401
