import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, ".env"))

# Historical placeholders that must never be accepted as signing material.
_DEV_JWT_FALLBACK = "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments"
_K8S_JWT_PLACEHOLDER = "placeholder-replace-via-kubectl-create-secret"
KNOWN_WEAK_JWT_SECRETS = frozenset({_DEV_JWT_FALLBACK, _K8S_JWT_PLACEHOLDER})


class Config(object):
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "todoapp")
    API_TITLE = "Rest API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.db")

    _jwt_from_env = (os.getenv("JWT_SECRET_KEY") or "").strip()
    JWT_SECRET_KEY = _jwt_from_env or None


class TestConfig(Config):
    pass
