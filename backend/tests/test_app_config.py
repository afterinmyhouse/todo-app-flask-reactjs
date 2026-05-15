from __future__ import annotations

import pytest

from config import DevelopmentConfig
from flaskr import create_app


def test_development_config_does_not_override_jwt_secret_with_fallback():
    assert "JWT_SECRET_KEY" not in DevelopmentConfig.__dict__


def test_non_testing_app_rejects_missing_jwt_secret():
    class MissingJwtConfig:
        TESTING = False
        JWT_SECRET_KEY = None

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(MissingJwtConfig)


def test_non_testing_app_rejects_short_jwt_secret():
    class ShortJwtConfig:
        TESTING = False
        JWT_SECRET_KEY = "too-short"

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(ShortJwtConfig)
