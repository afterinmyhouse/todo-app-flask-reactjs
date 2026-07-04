"""Security-focused startup checks for production-sensitive config."""

from __future__ import annotations

import pytest

from config import Config, DevelopmentConfig
from flaskr import create_app


class _RuntimeConfig(Config):
    TESTING = False


def _config_with_secret(secret):
    class _Config(_RuntimeConfig):
        JWT_SECRET_KEY = secret

    return _Config


@pytest.mark.parametrize(
    "secret",
    [
        None,
        "",
        "short-secret",
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
        "placeholder-replace-via-kubectl-create-secret",
    ],
)
def test_non_test_startup_rejects_missing_weak_or_committed_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_config_with_secret(secret))


def test_non_test_startup_accepts_strong_jwt_secret():
    app = create_app(_config_with_secret("x" * 32))

    assert app.config["JWT_SECRET_KEY"] == "x" * 32


def test_development_config_does_not_override_jwt_secret_with_fallback():
    assert "JWT_SECRET_KEY" not in DevelopmentConfig.__dict__
