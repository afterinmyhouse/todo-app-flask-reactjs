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


_KNOWN_PUBLIC_JWT_SECRETS = {
    "local-dev-insecure-set-JWT_SECRET_KEY-in-env-for-real-deployments",
    "placeholder-replace-via-kubectl-create-secret",
}


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(test_config)

    # Fail closed if signing material is missing or too short (non-test only).
    # See docs/security_review.md — weak/absent JWT_SECRET_KEY allows token forgery.
    jwt_secret = app.config.get("JWT_SECRET_KEY")
    if not app.config.get("TESTING"):
        normalized_jwt_secret = str(jwt_secret or "").strip()
        if (
            len(normalized_jwt_secret) < 32
            or normalized_jwt_secret in _KNOWN_PUBLIC_JWT_SECRETS
        ):
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a strong, private value "
                "(at least 32 characters). "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

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
