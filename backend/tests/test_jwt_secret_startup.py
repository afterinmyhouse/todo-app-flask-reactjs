"""Startup checks for JWT signing material."""

from typing import Optional

import pytest

from config import Config, JWT_INSECURE_SECRET_VALUES, TestConfig
from flaskr import create_app


def _config_with_secret(secret: Optional[str]):
    class _Config(Config):
        TESTING = False
        JWT_SECRET_KEY = secret

    return _Config


@pytest.mark.parametrize("secret", [None, "", "short-secret", "x" * 31])
def test_non_testing_app_rejects_missing_or_short_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_config_with_secret(secret))


@pytest.mark.parametrize("secret", sorted(JWT_INSECURE_SECRET_VALUES))
def test_non_testing_app_rejects_public_jwt_secret_values(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_config_with_secret(secret))


def test_non_testing_app_accepts_strong_private_jwt_secret():
    app = create_app(_config_with_secret("s" * 64))

    assert app.config["JWT_SECRET_KEY"] == "s" * 64


def test_testing_app_can_use_short_jwt_secret():
    class _Config(TestConfig):
        TESTING = True
        JWT_SECRET_KEY = "test-secret"

    app = create_app(_Config)

    assert app.config["JWT_SECRET_KEY"] == "test-secret"
