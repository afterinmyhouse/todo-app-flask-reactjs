from flask_jwt_extended import get_jwt_identity
from flaskr.errors import ErrorCode, api_abort
from flaskr.utils import generate_password
from flaskr.mongo import get_db
from bson import ObjectId


class UserController:
    @staticmethod
    def get_all():
        db = get_db()
        users = list(db.users.find({}, {"username": 1, "email": 1}))
        return [{"id": str(u["_id"]), "username": u["username"], "email": u["email"]} for u in users]

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        try:
            oid = ObjectId(user_id)
        except Exception:
            api_abort(404, ErrorCode.USER_NOT_FOUND, "User not found", details={"resource": "user"})

        user = db.users.find_one({"_id": oid}, {"username": 1, "email": 1})
        if not user:
            api_abort(404, ErrorCode.USER_NOT_FOUND, "User not found", details={"resource": "user"})
        return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}

    @staticmethod
    def create(data):
        db = get_db()

        if db.users.find_one({"username": data["username"]}):
            api_abort(
                409,
                ErrorCode.USERNAME_TAKEN,
                "Username already registered",
                details={"field": "username"},
            )
        if db.users.find_one({"email": data["email"]}):
            api_abort(
                409,
                ErrorCode.EMAIL_TAKEN,
                "Email already registered",
                details={"field": "email"},
            )

        doc = {
            "username": data["username"],
            "email": data["email"],
            "password": generate_password(data["password"]),
        }
        result = db.users.insert_one(doc)
        return {"id": str(result.inserted_id), "username": data["username"], "email": data["email"]}

    @staticmethod
    def delete():
        db = get_db()
        user_id = get_jwt_identity()
        try:
            oid = ObjectId(user_id)
        except Exception:
            api_abort(404, ErrorCode.USER_NOT_FOUND, "User not found", details={"resource": "user"})

        result = db.users.delete_one({"_id": oid})
        if result.deleted_count == 0:
            api_abort(404, ErrorCode.USER_NOT_FOUND, "User not found", details={"resource": "user"})
        return ""
