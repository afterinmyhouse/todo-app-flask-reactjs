from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from flask.views import MethodView
from flaskr.controllers.user_controller import UserController
from flaskr.errors import ErrorCode, api_abort
from flaskr.schemas.schema import UserSchema

bp = Blueprint("users", __name__)


@bp.route("/users")
class Users(MethodView):
    @jwt_required()
    @bp.response(200, UserSchema(many=True))
    def get(self):
        """Protected: only authenticated clients may list users."""
        return UserController.get_all()

    @bp.arguments(UserSchema)
    @bp.response(201)
    def post(self, data):
        return UserController.create(data)


@bp.route("/users/<user_id>")
class UserById(MethodView):
    @jwt_required()
    @bp.response(200, UserSchema)
    def get(self, user_id):
        """Protected: callers may only read their own user document."""
        if get_jwt_identity() != user_id:
            api_abort(
                403,
                ErrorCode.ACCESS_DENIED,
                "Forbidden",
                details={"resource": "user", "action": "read"},
            )
        return UserController.get_by_id(user_id)


@bp.route("/users/account")
class UserAccount(MethodView):
    @jwt_required()
    @bp.response(204)
    def delete(self):
        """Protected route (JWT Required)"""
        return UserController.delete()
