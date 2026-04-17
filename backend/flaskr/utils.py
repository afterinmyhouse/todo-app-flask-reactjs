from __future__ import annotations

from bson import ObjectId
from bson.errors import InvalidId
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.errors import ErrorCode, api_abort


def generate_password(password):
    return generate_password_hash(password, salt_length=10)


def check_password(password_hash, password):
    return check_password_hash(password_hash, password)


def resolve_user_oid() -> ObjectId:
    """Return the caller's user ObjectId from the JWT subject, or abort 401.

    Centralizes the identity parsing previously duplicated across controllers
    (project/task/task-comment). Keeps the 401 `INVALID_TOKEN_SUBJECT` payload
    consistent for every endpoint that relies on `sub` being a Mongo id.
    """
    user_id = get_jwt_identity()
    try:
        return ObjectId(user_id)
    except (InvalidId, TypeError):
        api_abort(
            401,
            ErrorCode.INVALID_TOKEN_SUBJECT,
            "Invalid token",
            details={"field": "sub"},
        )


def parse_object_id(value: str, *, http_status: int, error_code: str, message: str, field: str) -> ObjectId:
    """Parse an input string into an ObjectId or raise a standardized API error."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        api_abort(http_status, error_code, message, details={"field": field})
