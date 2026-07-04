from flask import Flask
from config import DevelopmentConfig
from flaskr.extensions import api, cors, jwt

from flaskr.routes.auth_route import bp as auth_route
from flaskr.routes.user_route import bp as user_route
from flaskr.routes.tag_route import bp as tag_route
from flaskr.routes.task_route import bp as task_route
from flaskr.routes.project_route import bp as project_route
from flaskr.routes.project_with_tasks_route import bp as project_with_tasks_route
from flaskr.routes.task_comment_route import bp as task_comment_route
from flaskr.routes.search_route import bp as search_route


UNSAFE_JWT_SECRET_VALUES = {
    "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
    "placeholder-replace-via-kubectl-create-secret",
}


def _validate_jwt_secret(app: Flask) -> None:
    """Fail closed in non-test environments unless JWT signing material is strong."""
    if app.config.get("TESTING"):
        return

    jwt_secret = str(app.config.get("JWT_SECRET_KEY") or "").strip()
    if len(jwt_secret) < 32 or jwt_secret in UNSAFE_JWT_SECRET_VALUES:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a strong value (at least 32 characters). "
            'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
        )


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(test_config)

    # Fail closed if signing material is missing, weak, or known unsafe (non-test only).
    # See docs/security_review.md — weak/absent JWT_SECRET_KEY allows token forgery.
    _validate_jwt_secret(app)

    api.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    api.register_blueprint(auth_route, url_prefix="/api/v1")
    api.register_blueprint(user_route, url_prefix="/api/v1")
    api.register_blueprint(tag_route, url_prefix="/api/v1")
    api.register_blueprint(task_route, url_prefix="/api/v1")
    api.register_blueprint(project_route, url_prefix="/api/v1")
    api.register_blueprint(project_with_tasks_route, url_prefix="/api/v1")
    api.register_blueprint(task_comment_route, url_prefix="/api/v1")
    api.register_blueprint(search_route, url_prefix="/api/v1")

    return app
