import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, ".env"))

# Used only by DevelopmentConfig when JWT_SECRET_KEY is not set in the environment.
# Never deploy with this value — set JWT_SECRET_KEY in .env or your host secrets manager.
_DEV_JWT_FALLBACK = "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments"


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
    # Local `flask run`: create_app requires a 32+ char signing key. If .env is missing or
    # shorter, use a fixed dev default (replace with secrets.token_urlsafe(32) for staging).
    JWT_SECRET_KEY = (
        _jwt_from_env if len(_jwt_from_env) >= 32 else _DEV_JWT_FALLBACK
    )


class TestConfig(Config):
    pass
