"""Startup configuration checks for security-sensitive app settings."""

from __future__ import annotations

import pytest

from config import Config, INSECURE_JWT_SECRET_VALUES
from flaskr import create_app


def _config_with_secret(secret: str | None):
    class _Config(Config):
        TESTING = False
        JWT_SECRET_KEY = secret

    return _Config


@pytest.mark.parametrize(
    "secret",
    [
        None,
        "",
        "short-secret",
        *sorted(INSECURE_JWT_SECRET_VALUES),
    ],
)
def test_non_test_app_rejects_missing_weak_or_placeholder_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_config_with_secret(secret))


def test_non_test_app_accepts_unique_strong_jwt_secret():
    app = create_app(
        _config_with_secret("unit-test-unique-secret-value-1234567890")
    )

    assert app.config["JWT_SECRET_KEY"] == "unit-test-unique-secret-value-1234567890"
