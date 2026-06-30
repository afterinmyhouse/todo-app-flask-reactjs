import pytest

from config import Config
from flaskr import create_app


def _config_with_secret(secret):
    class _JwtConfig(Config):
        TESTING = False
        JWT_SECRET_KEY = secret

    return _JwtConfig


@pytest.mark.parametrize(
    "secret",
    [
        None,
        "",
        "short-secret",
        " " * 40,
        "a" * 31,
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
    ],
)
def test_non_test_startup_rejects_missing_short_and_placeholder_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_config_with_secret(secret))


def test_non_test_startup_accepts_strong_jwt_secret():
    app = create_app(_config_with_secret("a-strong-test-secret-value-of-32-chars"))

    assert app.config["JWT_SECRET_KEY"] == "a-strong-test-secret-value-of-32-chars"
