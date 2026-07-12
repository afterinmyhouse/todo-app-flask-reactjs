from pathlib import Path

import pytest

from config import TestConfig, UNSAFE_JWT_SECRET_VALUES
from flaskr import create_app


def _runtime_config(secret):
    class RuntimeConfig(TestConfig):
        TESTING = False
        JWT_SECRET_KEY = secret

    return RuntimeConfig


def test_non_test_startup_rejects_missing_jwt_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_runtime_config(None))


def test_non_test_startup_rejects_short_jwt_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_app(_runtime_config("short-secret"))


@pytest.mark.parametrize("secret", sorted(UNSAFE_JWT_SECRET_VALUES))
def test_non_test_startup_rejects_committed_jwt_secret_values(secret):
    with pytest.raises(RuntimeError, match="placeholder|example"):
        create_app(_runtime_config(secret))


def test_non_test_startup_accepts_strong_unlisted_jwt_secret():
    app = create_app(
        _runtime_config("test-runtime-secret-value-that-is-long-enough")
    )

    assert app.config["JWT_SECRET_KEY"] == "test-runtime-secret-value-that-is-long-enough"


def test_committed_kubernetes_jwt_placeholder_is_not_bootable():
    manifest = Path(__file__).resolve().parents[2] / "k8s" / "backend.yaml"
    text = manifest.read_text(encoding="utf-8")

    assert 'JWT_SECRET_KEY: "replace-me"' in text
    assert "placeholder-replace-via-kubectl-create-secret" not in text
