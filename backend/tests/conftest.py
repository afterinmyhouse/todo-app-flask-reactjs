"""Shared pytest fixtures for the Flask backend test suite.

Design notes (kept intentionally small and dependency-free):

* `FakeCollection` implements the subset of the PyMongo `Collection` API
  our controllers actually use (`find_one`, `insert_one`). This lets the
  whole test suite run without MongoDB or `mongomock` installed.
* `FakeDb` auto-creates collections on attribute access so adding a new
  endpoint that persists to a new collection does not require editing
  this file.
* `fake_db` patches `flaskr.mongo.get_db` once. Controllers must import
  the `mongo` module (`from flaskr import mongo`) rather than binding
  `get_db` at import time so a single patch applies everywhere.
* The `app` fixture is session-scoped because `create_app` is pure and
  the tests never mutate config. This keeps the suite fast as the
  number of endpoints grows.
"""

from __future__ import annotations

from typing import Any

import pytest
from bson import ObjectId
from flask_jwt_extended import create_access_token

from config import TestConfig
from flaskr import create_app


class _InsertResult:
    def __init__(self, inserted_id: ObjectId):
        self.inserted_id = inserted_id


class _DeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class FakeCollection:
    """Minimal in-memory stand-in for a PyMongo collection.

    Intentionally supports only the surface area our controllers exercise:
    ``find_one``, ``insert_one``, and ``delete_one``. Plus a small test
    helper ``insert`` for seeding documents inside tests.
    """

    def __init__(self) -> None:
        self._docs: list[dict] = []

    def _matches(self, doc: dict, query: dict) -> bool:
        return all(doc.get(key) == value for key, value in query.items())

    def find_one(self, query: dict) -> dict | None:
        for doc in self._docs:
            if self._matches(doc, query):
                return doc
        return None

    def insert_one(self, doc: dict) -> _InsertResult:
        stored = dict(doc)
        stored.setdefault("_id", ObjectId())
        self._docs.append(stored)
        return _InsertResult(stored["_id"])

    def delete_one(self, query: dict) -> _DeleteResult:
        for index, doc in enumerate(self._docs):
            if self._matches(doc, query):
                del self._docs[index]
                return _DeleteResult(1)
        return _DeleteResult(0)

    def insert(self, doc: dict) -> ObjectId:
        """Test helper: seed a document and return its id."""
        return self.insert_one(doc).inserted_id

    @property
    def docs(self) -> list[dict]:
        return self._docs


class FakeDb:
    """Auto-provisioning fake Mongo DB. ``db.<anything>`` returns a FakeCollection."""

    def __init__(self) -> None:
        self._collections: dict[str, FakeCollection] = {}

    def __getattr__(self, name: str) -> FakeCollection:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._collections.setdefault(name, FakeCollection())


@pytest.fixture(scope="session")
def app() -> Any:
    class _TestConfig(TestConfig):
        TESTING = True
        JWT_SECRET_KEY = "test-secret"

    return create_app(_TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def fake_db(monkeypatch):
    db = FakeDb()
    monkeypatch.setattr("flaskr.mongo.get_db", lambda: db)
    return db


@pytest.fixture()
def auth_header(app):
    """Build an ``Authorization: Bearer <jwt>`` header. Defaults to a valid ObjectId subject."""

    def _build(user_id: str | None = None) -> dict[str, str]:
        identity = user_id if user_id is not None else str(ObjectId())
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _build
