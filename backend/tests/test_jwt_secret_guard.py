import pytest

from config import TestConfig
from flaskr import create_app


class _RuntimeConfig(TestConfig):
    TESTING = False
    JWT_SECRET_KEY = "a-private-signing-key-with-at-least-32-chars"


def test_runtime_app_accepts_private_jwt_secret():
    app = create_app(_RuntimeConfig)

    assert app.config["JWT_SECRET_KEY"] == _RuntimeConfig.JWT_SECRET_KEY


@pytest.mark.parametrize(
    "jwt_secret",
    [
        None,
        "",
        "short-secret",
        "placeholder-replace-via-kubectl-create-secret",
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
    ],
)
def test_runtime_app_rejects_missing_weak_or_public_jwt_secret(jwt_secret):
    class _BadRuntimeConfig(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = jwt_secret

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_BadRuntimeConfig)
