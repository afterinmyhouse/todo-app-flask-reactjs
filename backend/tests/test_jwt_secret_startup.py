from __future__ import annotations

import pytest

from config import INSECURE_JWT_SECRET_KEYS
from flaskr import create_app


class _BaseNonTestConfig:
    TESTING = False
    JWT_SECRET_KEY = "x" * 32
    API_TITLE = "Rest API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


@pytest.mark.parametrize(
    "secret",
    [
        None,
        "short-secret",
        next(iter(INSECURE_JWT_SECRET_KEYS)),
    ],
)
def test_non_test_app_rejects_missing_short_or_known_insecure_jwt_secret(secret):
    class _Config(_BaseNonTestConfig):
        JWT_SECRET_KEY = secret

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_Config)
