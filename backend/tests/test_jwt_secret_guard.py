"""Regression tests for JWT signing-secret startup validation."""

from __future__ import annotations

import pytest

from config import TestConfig
from flaskr import create_app


def _runtime_config(secret: str | None):
    class _RuntimeConfig(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = secret

    return _RuntimeConfig


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
def test_runtime_rejects_missing_short_or_public_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="strong, private"):
        create_app(_runtime_config(secret))


def test_runtime_accepts_private_jwt_secret():
    app = create_app(
        _runtime_config("test-only-private-signing-secret-with-32-plus-chars")
    )

    assert app.config["JWT_SECRET_KEY"] == (
        "test-only-private-signing-secret-with-32-plus-chars"
    )
