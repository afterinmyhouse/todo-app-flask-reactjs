from flask import Flask
from config import DevelopmentConfig, INSECURE_JWT_SECRET_VALUES
from flaskr.extensions import api, cors, jwt

from flaskr.routes.auth_route import bp as auth_route
from flaskr.routes.user_route import bp as user_route
from flaskr.routes.tag_route import bp as tag_route
from flaskr.routes.task_route import bp as task_route
from flaskr.routes.project_route import bp as project_route
from flaskr.routes.project_with_tasks_route import bp as project_with_tasks_route
from flaskr.routes.task_comment_route import bp as task_comment_route
from flaskr.routes.search_route import bp as search_route


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(test_config)

    # Fail closed if signing material is missing, weak, or a committed placeholder.
    # See docs/security_review.md — weak/predictable JWT_SECRET_KEY allows token forgery.
    jwt_secret = app.config.get("JWT_SECRET_KEY")
    if not app.config.get("TESTING"):
        jwt_secret_value = str(jwt_secret).strip() if jwt_secret is not None else ""
        if (
            not jwt_secret_value
            or len(jwt_secret_value) < 32
            or jwt_secret_value in INSECURE_JWT_SECRET_VALUES
        ):
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a unique strong value (at least 32 characters, "
                "not a committed placeholder). "
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
