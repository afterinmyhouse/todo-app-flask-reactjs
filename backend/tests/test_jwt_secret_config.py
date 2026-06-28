import pytest

from config import TestConfig
from flaskr import create_app


@pytest.mark.parametrize(
    "jwt_secret",
    [
        None,
        "",
        "short-secret",
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
        "placeholder-replace-via-kubectl-create-secret",
    ],
)
def test_non_test_app_rejects_missing_weak_or_known_jwt_secret(jwt_secret):
    class _Config(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = jwt_secret

    with pytest.raises(RuntimeError, match="strong, non-placeholder"):
        create_app(_Config)


def test_non_test_app_accepts_strong_non_placeholder_jwt_secret():
    class _Config(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = "a-secure-random-secret-value-32-chars"

    app = create_app(_Config)

    assert app.config["JWT_SECRET_KEY"] == _Config.JWT_SECRET_KEY
