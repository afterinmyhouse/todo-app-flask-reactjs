"""JWT-scoped workspace search for tasks, tags, and projects.

Used by the in-app assistant to enrich answers with structured hits from the
user's data (no external search APIs). Regex input is escaped to avoid ReDoS.
"""

from __future__ import annotations

import re

from flaskr import mongo
from flaskr.errors import api_abort
from flaskr.utils import resolve_user_oid


def _regex_fragment(raw: str) -> dict:
    """Build a case-insensitive Mongo regex clause from user text (escaped)."""
    return {"$regex": re.escape(raw), "$options": "i"}


class SearchController:
    MAX_QUERY_LEN = 120
    MIN_QUERY_LEN = 2
    TASK_LIMIT = 15
    TAG_LIMIT = 10
    PROJECT_LIMIT = 10

    @staticmethod
    def search(query: str) -> dict:
        q = (query or "").strip()
        if len(q) > SearchController.MAX_QUERY_LEN:
            api_abort(
                400,
                "BAD_REQUEST",
                "Search query too long",
                details={"field": "q", "max": SearchController.MAX_QUERY_LEN},
            )

        db = mongo.get_db()
        user_oid = resolve_user_oid()

        if len(q) < SearchController.MIN_QUERY_LEN:
            return {
                "query": q,
                "results": {"tags": [], "tasks": [], "projects": []},
            }

        pat = _regex_fragment(q)

        task_cursor = db.tasks.find(
            {
                "user_id": user_oid,
                "$or": [{"title": pat}, {"content": pat}],
            },
            {"title": 1, "status": 1, "tag_name": 1},
        ).limit(SearchController.TASK_LIMIT)

        tasks = []
        for doc in task_cursor:
            content = doc.get("content") or ""
            snippet = (content[:120] + "…") if len(content) > 120 else content
            tasks.append(
                {
                    "id": str(doc["_id"]),
                    "title": doc.get("title", ""),
                    "status": doc.get("status", ""),
                    "tag_name": doc.get("tag_name"),
                    "snippet": snippet,
                }
            )

        tag_cursor = db.tags.find({"name": pat}, {"name": 1}).limit(SearchController.TAG_LIMIT)
        tags = [{"id": str(doc["_id"]), "name": doc.get("name", "")} for doc in tag_cursor]

        project_cursor = db.projects.find(
            {
                "user_id": user_oid,
                "$or": [{"name": pat}, {"description": pat}],
            },
            {"name": 1, "description": 1},
        ).limit(SearchController.PROJECT_LIMIT)
        projects = [
            {
                "id": str(doc["_id"]),
                "name": doc.get("name", ""),
                "description": (doc.get("description") or "")[:160],
            }
            for doc in project_cursor
        ]

        return {"query": q, "results": {"tags": tags, "tasks": tasks, "projects": projects}}
