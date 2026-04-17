from __future__ import annotations

from datetime import datetime, timezone

from flaskr import mongo
from flaskr.errors import ErrorCode, api_abort
from flaskr.utils import resolve_user_oid


class ProjectController:
    @staticmethod
    def create(data: dict) -> dict:
        """Create a project for the authenticated user and return the created resource."""
        db = mongo.get_db()
        user_oid = resolve_user_oid()

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
