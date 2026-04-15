from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database

from config import Config

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return a process-wide MongoClient (singleton)."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_db() -> Database:
    """Default database for todo API collections."""
    return get_mongo_client()[Config.MONGO_DB_NAME]
