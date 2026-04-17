"""Controller for POST /api/v1/add-task-comment.

Mirrors the structure of :class:`flaskr.controllers.project_controller.ProjectController`
but relies on the shared :func:`flaskr.utils.resolve_user_oid` and
:func:`flaskr.utils.parse_object_id` helpers to avoid re-implementing
JWT/ObjectId error handling per endpoint.
"""

from __future__ import annotations

from datetime import datetime, timezone

from flaskr import mongo
from flaskr.errors import ErrorCode, api_abort
from flaskr.utils import parse_object_id, resolve_user_oid


class TaskCommentController:
    @staticmethod
    def create(data: dict) -> dict:
        """Create a comment on a task the authenticated user owns."""
        db = mongo.get_db()
        user_oid = resolve_user_oid()

        task_oid = parse_object_id(
            data["task_id"],
            http_status=400,
            error_code=ErrorCode.INVALID_TASK,
            message="Invalid task",
            field="taskId",
        )

        # Authorization + existence check in a single query: a user can only
        # comment on tasks they own. Anything else is reported as 404 to
        # avoid leaking whether the task exists under another account.
        task = db.tasks.find_one({"_id": task_oid, "user_id": user_oid})
        if not task:
            api_abort(
                404,
                ErrorCode.TASK_NOT_FOUND,
                "Task not found",
                details={"resource": "task"},
            )

        body = data["body"].strip()
        if not body:
            api_abort(
                422,
                "VALIDATION_ERROR",
                "Unprocessable Entity",
                details={"validation": {"json": {"body": ["Must not be blank."]}}},
            )

        doc = {
            "task_id": task_oid,
            "user_id": user_oid,
            "body": body,
            "created_at": datetime.now(timezone.utc),
        }
        result = db.task_comments.insert_one(doc)
        return {
            "id": str(result.inserted_id),
            "task_id": str(task_oid),
            "body": body,
            "created_at": doc["created_at"],
        }
