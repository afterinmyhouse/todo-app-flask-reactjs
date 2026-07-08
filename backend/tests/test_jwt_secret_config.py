"""Security regressions for JWT signing-key configuration."""

from __future__ import annotations

import pytest

from config import Config, DevelopmentConfig
from flaskr import create_app


def test_development_config_does_not_supply_committed_jwt_fallback():
    assert DevelopmentConfig.JWT_SECRET_KEY == Config.JWT_SECRET_KEY


@pytest.mark.parametrize("secret", [None, "", "too-short"])
def test_non_testing_app_rejects_missing_or_weak_jwt_secret(secret):
    class _UnsafeConfig(Config):
        TESTING = False
        JWT_SECRET_KEY = secret

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        create_app(_UnsafeConfig)
