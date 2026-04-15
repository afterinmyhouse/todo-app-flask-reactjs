from flask_jwt_extended import get_jwt_identity
from flaskr.errors import ErrorCode, api_abort
from flaskr.mongo import get_db
from bson import ObjectId
from datetime import datetime, timezone


class TaskController:
    @staticmethod
    def get_all_on_user():
        db = get_db()
        user_id = get_jwt_identity()
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            api_abort(
                401,
                ErrorCode.INVALID_TOKEN_SUBJECT,
                "Invalid token",
                details={"field": "sub"},
            )

        tasks = list(db.tasks.find({"user_id": user_oid}))
        return [
            {
                "id": str(t["_id"]),
                "title": t["title"],
                "content": t["content"],
                "status": t["status"],
                "createdAt": t["created_at"],
                "tagName": t["tag_name"],
            }
            for t in tasks
        ]

    @staticmethod
    def create(data):
        db = get_db()
        user_id = get_jwt_identity()
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            api_abort(
                401,
                ErrorCode.INVALID_TOKEN_SUBJECT,
                "Invalid token",
                details={"field": "sub"},
            )

        try:
            tag_oid = ObjectId(data["tag_id"])
        except Exception:
            api_abort(400, ErrorCode.INVALID_TAG, "Invalid tag", details={"field": "tagId"})

        tag = db.tags.find_one({"_id": tag_oid})
        if not tag:
            api_abort(404, ErrorCode.TAG_NOT_FOUND, "Tag not found", details={"resource": "tag"})

        doc = {
            "title": data["title"],
            "content": data["content"],
            "status": data["status"],
            "created_at": datetime.now(timezone.utc),
            "user_id": user_oid,
            "tag_id": tag_oid,
            "tag_name": tag["name"],
        }
        db.tasks.insert_one(doc)
        return ""

    @staticmethod
    def update(data, task_id):
        db = get_db()
        user_id = get_jwt_identity()
        try:
            user_oid = ObjectId(user_id)
            task_oid = ObjectId(task_id)
        except Exception:
            api_abort(404, ErrorCode.TASK_NOT_FOUND, "Task not found", details={"resource": "task"})

        result = db.tasks.update_one(
            {"_id": task_oid, "user_id": user_oid},
            {"$set": {"title": data["title"], "content": data["content"], "status": data["status"]}},
        )
        if result.matched_count == 0:
            api_abort(404, ErrorCode.TASK_NOT_FOUND, "Task not found", details={"resource": "task"})
        return ""

    @staticmethod
    def delete(task_id):
        db = get_db()
        user_id = get_jwt_identity()
        try:
            user_oid = ObjectId(user_id)
            task_oid = ObjectId(task_id)
        except Exception:
            api_abort(404, ErrorCode.TASK_NOT_FOUND, "Task not found", details={"resource": "task"})

        result = db.tasks.delete_one({"_id": task_oid, "user_id": user_oid})
        if result.deleted_count == 0:
            api_abort(404, ErrorCode.TASK_NOT_FOUND, "Task not found", details={"resource": "task"})
        return ""
