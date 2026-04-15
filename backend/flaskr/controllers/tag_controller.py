from flaskr.errors import ErrorCode, api_abort
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
            api_abort(
                409,
                ErrorCode.TAG_EXISTS,
                "Tag already registered",
                details={"field": "name"},
            )

        result = db.tags.insert_one({"name": data["name"]})
        return {"id": str(result.inserted_id), "name": data["name"]}
