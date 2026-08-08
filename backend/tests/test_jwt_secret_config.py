"""Regression tests for JWT signing-key startup validation."""

from __future__ import annotations

import pytest

from config import DevelopmentConfig, TestConfig
from flaskr import create_app


def _runtime_config(secret: object, testing: bool = False):
    class RuntimeConfig(DevelopmentConfig):
        TESTING = testing
        JWT_SECRET_KEY = secret

    return RuntimeConfig


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
def test_non_test_startup_rejects_missing_weak_or_public_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_runtime_config(secret))


def test_non_test_startup_accepts_strong_private_jwt_secret():
    app = create_app(_runtime_config("a-private-test-secret-with-at-least-32-chars"))

    assert app.config["JWT_SECRET_KEY"] == "a-private-test-secret-with-at-least-32-chars"


def test_testing_config_can_use_short_test_secret():
    class RuntimeTestConfig(TestConfig):
        TESTING = True
        JWT_SECRET_KEY = "test-secret"

    app = create_app(RuntimeTestConfig)

    assert app.config["JWT_SECRET_KEY"] == "test-secret"


def test_development_config_does_not_define_committed_jwt_fallback():
    import config as config_module

    assert not hasattr(config_module, "_DEV_JWT_FALLBACK")
    # DevelopmentConfig must inherit env-only JWT_SECRET_KEY (no hardcoded fallback).
    assert "JWT_SECRET_KEY" not in DevelopmentConfig.__dict__
