from flask_smorest import abort
from flaskr.mongo import get_db


class TagController:
    @staticmethod
    def get_all():
        db = get_db()
        tags = list(db.tags.find({}, {"name": 1}).limit(50))
        return [{"id": str(t["_id"]), "name": t["name"]} for t in tags]

    @staticmethod
    def create(data):
        db = get_db()
        if db.tags.find_one({"name": data["name"]}):
            abort(409, message="Tag already registered")

        result = db.tags.insert_one({"name": data["name"]})
        return {"id": str(result.inserted_id), "name": data["name"]}
