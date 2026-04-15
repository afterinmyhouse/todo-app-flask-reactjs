from flask import jsonify
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from flaskr.errors import ErrorCode, default_code_for_http_status

cors = CORS()
jwt = JWTManager()


def _jwt_error_payload(code: str, message: str, http_status: int) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "httpStatus": http_status,
            "details": {},
        }
    }


@jwt.unauthorized_loader
def _jwt_unauthorized(_reason: str):
    body = _jwt_error_payload(ErrorCode.AUTH_REQUIRED, "Authentication required", 401)
    return jsonify(body), 401


@jwt.invalid_token_loader
def _jwt_invalid(_error: str):
    body = _jwt_error_payload(ErrorCode.INVALID_TOKEN, "Invalid token", 401)
    return jsonify(body), 401


@jwt.expired_token_loader
def _jwt_expired(_jwt_header, _jwt_payload):
    body = _jwt_error_payload(ErrorCode.TOKEN_EXPIRED, "Token has expired", 401)
    return jsonify(body), 401


class TodoAppApi(Api):
    """flask-smorest API with a single JSON error envelope (see docs/API_ERROR_HANDLING.md)."""

    def handle_http_exception(self, error: HTTPException):
        data = getattr(error, "data", None) or {}
        http_status = int(error.code)
        code = data.get("error_code") or default_code_for_http_status(http_status)
        message = data.get("message")
        if not message:
            desc = getattr(error, "description", None)
            message = (desc.strip() if isinstance(desc, str) and desc.strip() else None) or error.name
        details = dict(data.get("details") or {})
        if "errors" in data:
            details["validation"] = data["errors"]
        elif "messages" in data:
            details["validation"] = data["messages"]

        body = {
            "error": {
                "code": code,
                "message": message,
                "httpStatus": http_status,
                "details": details,
            }
        }
        headers = data.get("headers") or {}
        return jsonify(body), http_status, headers


api = TodoAppApi()
