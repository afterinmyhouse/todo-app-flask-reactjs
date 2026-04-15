# API error handling

This document describes how the TodoApp REST API (`/api/v1`) represents failures and how clients should read them.

## Response envelope

Every error response uses **HTTP status** (4xx/5xx) plus a **JSON body** with a single top-level object `error`:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found",
    "httpStatus": 404,
    "details": {
      "resource": "user"
    }
  }
}
```

| Field | Type | Meaning |
| ----- | ---- | ------- |
| `error.code` | string | Stable **machine-readable** identifier (see catalog below). |
| `error.message` | string | Human-readable summary for logs and UI. |
| `error.httpStatus` | integer | Same semantics as the HTTP status line (repeated for clients that only read the body). |
| `error.details` | object | Optional context (e.g. `resource`, or `validation` for schema errors). |

**Validation errors** (invalid JSON body or field validation) place field-level issues under `error.details.validation`, keyed by argument location (e.g. `json` → field name → list of messages), as produced by Marshmallow / flask-smorest.

## HTTP status usage

| Status | Typical `error.code` | When |
| ------ | -------------------- | ---- |
| `400` | `BAD_REQUEST`, `INVALID_TAG`, … | Malformed input or domain rule (e.g. invalid id). |
| `401` | `AUTH_REQUIRED`, `AUTH_INVALID_CREDENTIALS`, `TOKEN_EXPIRED`, `INVALID_TOKEN` | Missing/invalid JWT or failed login. |
| `403` | `ACCESS_DENIED` | Authenticated but not allowed for this resource. |
| `404` | `NOT_FOUND`, `USER_NOT_FOUND`, `TASK_NOT_FOUND`, `TAG_NOT_FOUND` | Resource missing. |
| `409` | `CONFLICT`, `USERNAME_TAKEN`, `EMAIL_TAKEN`, `TAG_EXISTS` | Unique constraint / duplicate. |
| `422` | `VALIDATION_ERROR` | Request body/query did not validate (if surfaced as 422). |

## Error code catalog (current)

Codes are **UPPER_SNAKE_CASE** strings. New endpoints should reuse existing codes when the situation matches; add new codes sparingly and update this table.

| `error.code` | HTTP | Description |
| ------------ | ---- | ----------- |
| `AUTH_REQUIRED` | 401 | No or non-Bearer `Authorization` on a protected route. |
| `INVALID_TOKEN` | 401 | JWT malformed or invalid. |
| `TOKEN_EXPIRED` | 401 | JWT past `exp`. |
| `AUTH_INVALID_CREDENTIALS` | 401 | Login email/password incorrect. |
| `ACCESS_DENIED` | 403 | JWT subject cannot access this resource (e.g. another user’s id). |
| `NOT_FOUND` | 404 | Generic not found (routing / fallback). |
| `USER_NOT_FOUND` | 404 | User id does not exist. |
| `TASK_NOT_FOUND` | 404 | Task id missing or not owned by caller. |
| `TAG_NOT_FOUND` | 404 | Tag id invalid or missing. |
| `INVALID_TAG` | 400 | Tag id format invalid. |
| `INVALID_TOKEN_SUBJECT` | 401 | JWT subject not a valid user id where required. |
| `CONFLICT` | 409 | Generic conflict. |
| `USERNAME_TAKEN` | 409 | Username already registered. |
| `EMAIL_TAKEN` | 409 | Email already registered. |
| `TAG_EXISTS` | 409 | Tag name already exists (`Tag already registered`). |

## Implementation rules (backend)

1. **Controllers and routes** should use `api_abort(...)` from `flaskr.errors` (or `abort(..., error_code=..., details=...)`) instead of bare `abort(status)` so `error.code` and `details` are always set.
2. **JWT** callbacks in `flaskr/extensions.py` return the **same** `error` envelope as application errors.
3. **flask-smorest** `Api` subclass (`TodoAppApi`) normalizes all `HTTPException` instances (including webargs `abort`) into the envelope above.

## Client guidance (frontend / mobile)

1. Prefer **`response.data.error.message`** for user-visible toasts; fall back to status text if missing.
2. Branch on **`response.data.error.code`** for i18n or retry logic (e.g. `TOKEN_EXPIRED` → refresh or redirect to login).
3. For `400`/`422`, read **`response.data.error.details.validation`** for per-field form errors.

## Security

- Do not put secrets or stack traces in `error.message` or `details` in production.
- Keep messages honest but not overly verbose (avoid leaking whether an email exists on login if product policy requires it; current login uses a generic message).
