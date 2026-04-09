import os
from pymongo import MongoClient


def get_mongo_client() -> MongoClient:
    """
    Lazily create a MongoClient using env vars.
    """
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri)


def get_db_name() -> str:
    return os.getenv("MONGO_DB_NAME", "todoapp")


def get_db():
    client = get_mongo_client()
    return client[get_db_name()]

