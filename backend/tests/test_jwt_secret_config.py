from __future__ import annotations

import pytest

from config import DevelopmentConfig
from flaskr import create_app


class _BaseNonTestConfig(DevelopmentConfig):
    TESTING = False


def _config_with_secret(secret: str | None):
    class _Config(_BaseNonTestConfig):
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
def test_non_test_startup_rejects_missing_short_or_public_jwt_secrets(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_config_with_secret(secret))


def test_non_test_startup_accepts_private_length_jwt_secret():
    app = create_app(_config_with_secret("a-private-test-secret-with-enough-entropy"))

    assert app.config["JWT_SECRET_KEY"] == "a-private-test-secret-with-enough-entropy"
