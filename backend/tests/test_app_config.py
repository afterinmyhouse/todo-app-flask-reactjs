import pytest

from config import KNOWN_WEAK_JWT_SECRETS, TestConfig
from flaskr import create_app


def test_create_app_accepts_strong_jwt_secret():
    class _StrongJwtConfig(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = "a-strong-test-secret-with-at-least-32-chars"

    app = create_app(_StrongJwtConfig)

    assert app.config["JWT_SECRET_KEY"] == _StrongJwtConfig.JWT_SECRET_KEY


@pytest.mark.parametrize(
    "secret",
    [None, "", "short-secret", *sorted(KNOWN_WEAK_JWT_SECRETS)],
)
def test_create_app_rejects_missing_short_and_placeholder_jwt_secrets(secret):
    class _WeakJwtConfig(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = secret

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_WeakJwtConfig)
