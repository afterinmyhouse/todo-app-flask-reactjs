from __future__ import annotations

import pytest
from bson import ObjectId
from flask_jwt_extended import create_access_token

from config import TestConfig
from flaskr import create_app


class _InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeProjectsCollection:
    def __init__(self):
        self._docs: list[dict] = []

    def find_one(self, query: dict):
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None

    def insert_one(self, doc: dict):
        stored = dict(doc)
        stored["_id"] = ObjectId()
        self._docs.append(stored)
        return _InsertResult(stored["_id"])


class FakeDb:
    def __init__(self):
        self.projects = FakeProjectsCollection()


@pytest.fixture()
def app():
    class _TestConfig(TestConfig):
        TESTING = True
        JWT_SECRET_KEY = "test-secret"

    return create_app(_TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def fake_db(monkeypatch):
    import flaskr.controllers.project_controller as project_controller

    db = FakeDb()
    monkeypatch.setattr(project_controller, "get_db", lambda: db)
    return db


@pytest.fixture()
def auth_header(app):
    def _build(user_id: str | None = None):
        identity = user_id or str(ObjectId())
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _build
