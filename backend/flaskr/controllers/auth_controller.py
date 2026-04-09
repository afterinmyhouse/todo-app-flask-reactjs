from flask_jwt_extended import create_access_token
from flask_smorest import abort
from flaskr.utils import check_password
from flaskr.mongo import get_db


class AuthController:
    @staticmethod
    def sign_in(data):
        db = get_db()
        user = db.users.find_one({"email": data["email"]})

        if user is None or check_password(user["password"], data["password"]) is False:
            abort(401, message="Incorrect credentials")

        token = create_access_token(identity=str(user["_id"]))

        return {"token": token}
