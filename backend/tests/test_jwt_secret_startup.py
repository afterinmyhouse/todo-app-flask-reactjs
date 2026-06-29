"""Startup guard tests for JWT signing material."""

from __future__ import annotations

import pytest

from config import Config
from flaskr import create_app


@pytest.mark.parametrize(
    "jwt_secret",
    [
        None,
        "",
        "short-secret",
        "c7d57142e46f169ce9dbeb8d96603e46",
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
        "placeholder-replace-via-kubectl-create-secret",
    ],
)
def test_create_app_rejects_missing_weak_or_public_jwt_secret(jwt_secret):
    class _RuntimeConfig(Config):
        TESTING = False
        JWT_SECRET_KEY = jwt_secret

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_RuntimeConfig)
