from flask_jwt_extended import get_jwt_identity
from flask_smorest import abort
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
            abort(404, message="User not found")

        user = db.users.find_one({"_id": oid}, {"username": 1, "email": 1})
        if not user:
            abort(404, message="User not found")
        return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}

    @staticmethod
    def create(data):
        db = get_db()

        if db.users.find_one({"username": data["username"]}):
            abort(409, message="Username already registered")
        if db.users.find_one({"email": data["email"]}):
            abort(409, message="Email already registered")

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
            abort(404, message="User not found")

        result = db.users.delete_one({"_id": oid})
        if result.deleted_count == 0:
            abort(404, message="User not found")
        return ""
