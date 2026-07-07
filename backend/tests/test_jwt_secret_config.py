import pytest

from config import DevelopmentConfig
from flaskr import create_app


def _config_with_secret(secret):
    return type(
        "_RuntimeConfig",
        (DevelopmentConfig,),
        {
            "TESTING": False,
            "JWT_SECRET_KEY": secret,
        },
    )


@pytest.mark.parametrize(
    "secret",
    [
        None,
        "",
        "short-secret",
        "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
        "placeholder-replace-via-kubectl-create-secret",
        "c7d57142e46f169ce9dbeb8d96603e46",
    ],
)
def test_non_test_app_rejects_missing_weak_or_committed_jwt_secret(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_config_with_secret(secret))


def test_non_test_app_accepts_strong_uncommitted_jwt_secret():
    app = create_app(_config_with_secret("a" * 64))

    assert app.config["JWT_SECRET_KEY"] == "a" * 64
