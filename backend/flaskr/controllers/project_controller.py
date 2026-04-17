from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask_jwt_extended import get_jwt_identity

from flaskr.errors import ErrorCode, api_abort
from flaskr.mongo import get_db


class ProjectController:
    @staticmethod
    def create(data):
        """Create a project for the authenticated user and return the created resource."""
        db = get_db()
        user_id = get_jwt_identity()

        try:
            user_oid = ObjectId(user_id)
        except InvalidId:
            api_abort(
                401,
                ErrorCode.INVALID_TOKEN_SUBJECT,
                "Invalid token",
                details={"field": "sub"},
            )

        normalized_name = data["name"].strip()
        if db.projects.find_one({"user_id": user_oid, "normalized_name": normalized_name.lower()}):
            api_abort(
                409,
                ErrorCode.PROJECT_EXISTS,
                "Project already exists",
                details={"field": "name"},
            )

        # Persist both display name and normalized key so duplicate checks remain
        # stable for case-only variations (e.g. "Alpha" vs "alpha").
        doc = {
            "name": normalized_name,
            "description": data.get("description", "").strip(),
            "created_at": datetime.now(timezone.utc),
            "user_id": user_oid,
            "normalized_name": normalized_name.lower(),
        }
        result = db.projects.insert_one(doc)
        return {
            "id": str(result.inserted_id),
            "name": doc["name"],
            "description": doc["description"],
            "created_at": doc["created_at"],
        }
