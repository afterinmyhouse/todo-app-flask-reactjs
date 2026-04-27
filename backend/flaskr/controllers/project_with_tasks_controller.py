"""Controller for POST /api/v1/add-project-with-tasks.

Design notes
------------

This endpoint creates **two related entities** — a project and its 1..50
initial tasks — in a single request. The controller is organized into
three explicit phases so the coordination logic stays readable even as
the request shape grows:

1. **Pre-validation.** Everything that can be checked *before* any write
   happens here: JWT subject parsing, duplicate-project-name check,
   duplicate-title-in-request check, ``tagId`` format validation, and
   existence of every referenced tag. Failing here yields a clean 4xx
   with no side effects.
2. **Persist.** Project first (so tasks can reference its ``_id``),
   then tasks one by one, tracking inserted ids.
3. **Compensation on partial failure.** If task insertion raises after
   the project (or earlier tasks) already landed, we delete what we
   inserted so the caller never observes a half-applied state. This is
   the pragmatic equivalent of a transaction for standalone MongoDB.
   On a replica-set deployment this block should be replaced with
   ``with client.start_session() as s: s.start_transaction(): ...``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId

from flaskr import mongo
from flaskr.errors import ErrorCode, api_abort
from flaskr.utils import parse_object_id, resolve_user_oid


def _strip_required_text(value: str, *, field_path: str) -> str:
    """Trim ``value`` and abort 422 if it is blank after trimming."""
    stripped = value.strip()
    if not stripped:
        api_abort(
            422,
            "VALIDATION_ERROR",
            "Unprocessable Entity",
            details={"validation": {"json": {field_path: ["Must not be blank."]}}},
        )
    return stripped


class ProjectWithTasksController:
    @staticmethod
    def create(data: dict) -> dict:
        db = mongo.get_db()
        user_oid = resolve_user_oid()

        # ----- Phase 1: pre-validation (no writes) ---------------------------
        project_name = _strip_required_text(data["name"], field_path="name")
        normalized_project_key = project_name.lower()
        if db.projects.find_one({"user_id": user_oid, "normalized_name": normalized_project_key}):
            api_abort(
                409,
                ErrorCode.PROJECT_EXISTS,
                "Project already exists",
                details={"field": "name"},
            )

        tasks_payload: list[dict[str, Any]] = data["tasks"]
        prepared_tasks, tag_resolution = _prepare_tasks(db, tasks_payload)

        # ----- Phase 2: persist ---------------------------------------------
        now = datetime.now(timezone.utc)
        project_doc = {
            "name": project_name,
            "description": data.get("description", "").strip(),
            "created_at": now,
            "user_id": user_oid,
            "normalized_name": normalized_project_key,
        }
        project_id = db.projects.insert_one(project_doc).inserted_id

        inserted_task_records: list[tuple[ObjectId, dict]] = []
        try:
            for prepared in prepared_tasks:
                tag_oid = prepared["tag_oid"]
                tag_name = tag_resolution[tag_oid]["name"] if tag_oid is not None else None
                task_doc = {
                    "title": prepared["title"],
                    "content": prepared["content"],
                    "status": prepared["status"],
                    "created_at": now,
                    "user_id": user_oid,
                    "project_id": project_id,
                    "tag_id": tag_oid,
                    "tag_name": tag_name,
                }
                task_id = db.tasks.insert_one(task_doc).inserted_id
                inserted_task_records.append((task_id, task_doc))
        except Exception:
            # ----- Phase 3: compensation -------------------------------------
            # Best-effort rollback: delete any tasks we inserted, then the
            # project. Failures inside the cleanup itself are swallowed so
            # the original exception still surfaces to the caller.
            for task_id, _ in inserted_task_records:
                try:
                    db.tasks.delete_one({"_id": task_id})
                except Exception:
                    pass
            try:
                db.projects.delete_one({"_id": project_id})
            except Exception:
                pass
            raise

        return {
            "id": str(project_id),
            "name": project_doc["name"],
            "description": project_doc["description"],
            "created_at": project_doc["created_at"],
            "tasks": [
                {
                    "id": str(task_id),
                    "title": doc["title"],
                    "content": doc["content"],
                    "status": doc["status"],
                    "tag_name": doc["tag_name"],
                    "created_at": doc["created_at"],
                }
                for task_id, doc in inserted_task_records
            ],
        }


def _prepare_tasks(db, tasks_payload: list[dict[str, Any]]):
    """Validate the tasks sub-payload and resolve referenced tags.

    Returns a tuple ``(prepared_tasks, tag_resolution)`` where:

    * ``prepared_tasks`` is a list of dicts with normalized fields
      (``title``, ``content``, ``status``, ``tag_oid``) in request order.
    * ``tag_resolution`` maps ``ObjectId`` → tag document for every
      distinct ``tagId`` referenced, allowing the persistence loop to
      stamp ``tag_name`` without re-querying per task.

    All validation errors surface before any write happens.
    """
    seen_title_keys: set[str] = set()
    prepared: list[dict[str, Any]] = []
    distinct_tag_oids: dict[str, ObjectId] = {}

    for index, raw_task in enumerate(tasks_payload):
        title = _strip_required_text(raw_task["title"], field_path=f"tasks[{index}].title")
        title_key = title.lower()
        if title_key in seen_title_keys:
            api_abort(
                422,
                ErrorCode.DUPLICATE_TASK_TITLE,
                "Duplicate task title in request",
                details={"field": f"tasks[{index}].title", "value": title},
            )
        seen_title_keys.add(title_key)

        tag_raw = raw_task.get("tag_id")
        tag_oid: Optional[ObjectId] = None
        if tag_raw:
            if tag_raw not in distinct_tag_oids:
                distinct_tag_oids[tag_raw] = parse_object_id(
                    tag_raw,
                    http_status=400,
                    error_code=ErrorCode.INVALID_TAG,
                    message="Invalid tag",
                    field=f"tasks[{index}].tagId",
                )
            tag_oid = distinct_tag_oids[tag_raw]

        prepared.append(
            {
                "title": title,
                "content": (raw_task.get("content") or "").strip(),
                "status": raw_task.get("status") or "PENDING",
                "tag_oid": tag_oid,
            }
        )

    # Resolve every distinct referenced tag exactly once. Using find_one
    # per distinct tag (rather than a single ``$in`` query) keeps the
    # in-memory test collection simple; for very large tag sets this is
    # the natural place to switch to a batched lookup.
    tag_resolution: dict[ObjectId, dict] = {}
    for raw, oid in distinct_tag_oids.items():
        doc = db.tags.find_one({"_id": oid})
        if not doc:
            api_abort(
                404,
                ErrorCode.TAG_NOT_FOUND,
                "Tag not found",
                details={"resource": "tag", "field": "tagId", "value": raw},
            )
        tag_resolution[oid] = doc

    return prepared, tag_resolution
