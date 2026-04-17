"""Central API error codes and `api_abort` helper (see docs/API_ERROR_HANDLING.md)."""

from __future__ import annotations

from flask_smorest import abort as smorest_abort


class ErrorCode:
    AUTH_REQUIRED = "AUTH_REQUIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    INVALID_TOKEN_SUBJECT = "INVALID_TOKEN_SUBJECT"
    ACCESS_DENIED = "ACCESS_DENIED"
    NOT_FOUND = "NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TAG_NOT_FOUND = "TAG_NOT_FOUND"
    INVALID_TAG = "INVALID_TAG"
    INVALID_TASK = "INVALID_TASK"
    PROJECT_EXISTS = "PROJECT_EXISTS"
    DUPLICATE_TASK_TITLE = "DUPLICATE_TASK_TITLE"
    CONFLICT = "CONFLICT"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    EMAIL_TAKEN = "EMAIL_TAKEN"
    TAG_EXISTS = "TAG_EXISTS"


def api_abort(
    http_status: int,
    error_code: str,
    message: str,
    details: dict | None = None,
) -> None:
    """Raise HTTPException consumed by :class:`TodoAppApi` into the standard `error` JSON envelope."""
    smorest_abort(
        http_status,
        message=message,
        error_code=error_code,
        details=details or {},
    )


def default_code_for_http_status(status: int) -> str:
    if status == 400:
        return "BAD_REQUEST"
    if status == 401:
        return "UNAUTHORIZED"
    if status == 403:
        return "FORBIDDEN"
    if status == 404:
        return ErrorCode.NOT_FOUND
    if status == 409:
        return ErrorCode.CONFLICT
    if status == 422:
        return "VALIDATION_ERROR"
    if status >= 500:
        return "INTERNAL_ERROR"
    return "ERROR"
