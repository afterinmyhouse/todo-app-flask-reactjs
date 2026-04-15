from flask_jwt_extended import create_access_token, get_jwt_identity
from flaskr.controllers.user_controller import UserController
from flaskr.errors import ErrorCode, api_abort
from flaskr.utils import check_password
from flaskr.mongo import get_db


class AuthController:
    @staticmethod
    def login(data):
        """Validate email/password and return a JWT access token (subject = user ObjectId string)."""
        db = get_db()
        user = db.users.find_one({"email": data["email"]})

        if user is None or check_password(user["password"], data["password"]) is False:
            api_abort(
                401,
                ErrorCode.AUTH_INVALID_CREDENTIALS,
                "Incorrect credentials",
                details={"reason": "email_or_password"},
            )

        token = create_access_token(identity=str(user["_id"]))
        return {"token": token}

    @staticmethod
    def sign_in(data):
        """Legacy alias for :meth:`login` (same behavior)."""
        return AuthController.login(data)

    @staticmethod
    def register(data):
        """Create account and return user fields plus JWT (same persistence rules as POST /users)."""
        created = UserController.create(data)
        token = create_access_token(identity=created["id"])
        return {**created, "token": token}

    @staticmethod
    def me():
        """Current user profile derived from JWT subject (MongoDB ObjectId string)."""
        return UserController.get_by_id(get_jwt_identity())
