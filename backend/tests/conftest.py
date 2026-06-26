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

import re
from typing import Any, Optional

import pytest
from bson import ObjectId
from flask_jwt_extended import create_access_token

from config import TestConfig
from flaskr import create_app


def _mongo_field_matches(doc: dict, key: str, cond: object) -> bool:
    if isinstance(cond, dict) and "$regex" in cond:
        text = str(doc.get(key, "") or "")
        flags = re.IGNORECASE if "i" in str(cond.get("$options", "")) else 0
        return re.search(str(cond["$regex"]), text, flags) is not None
    return doc.get(key) == cond


def _mongo_clause_matches(doc: dict, clause: dict) -> bool:
    return all(_mongo_field_matches(doc, k, v) for k, v in clause.items())


def _mongo_query_matches(doc: dict, query: dict) -> bool:
    for key, val in query.items():
        if key == "$or":
            if not any(_mongo_clause_matches(doc, sub) for sub in val):
                return False
        else:
            if not _mongo_field_matches(doc, key, val):
                return False
    return True


def _mongo_project(doc: dict, projection: dict) -> dict:
    if projection is None:
        return dict(doc)
    out: dict = {}
    if projection.get("_id", 1) != 0:
        out["_id"] = doc.get("_id")
    for key, flag in projection.items():
        if key == "_id":
            continue
        if flag == 1 and key in doc:
            out[key] = doc[key]
    return out


class FakeCursor:
    """Minimal stand-in for a PyMongo cursor supporting ``limit`` and iteration."""

    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def limit(self, n: int) -> FakeCursor:
        return FakeCursor(self._docs[:n])

    def __iter__(self):
        return iter(self._docs)


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

    def find_one(self, query: dict) -> Optional[dict]:
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

    def find(self, query: dict, projection: Optional[dict] = None) -> FakeCursor:
        matched: list[dict] = []
        for doc in self._docs:
            if _mongo_query_matches(doc, query):
                matched.append(_mongo_project(doc, projection) if projection else dict(doc))
        return FakeCursor(matched)

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
        JWT_SECRET_KEY = "test-secret-with-at-least-32-characters"

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

    def _build(user_id: Optional[str] = None) -> dict[str, str]:
        identity = user_id if user_id is not None else str(ObjectId())
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _build
