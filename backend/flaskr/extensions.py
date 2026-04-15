from flask import jsonify
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

api = Api()
cors = CORS()
jwt = JWTManager()


@jwt.unauthorized_loader
def _jwt_unauthorized(_reason: str):
    """Missing or malformed `Authorization: Bearer` for a protected route."""
    return jsonify(message="Authentication required"), 401


@jwt.invalid_token_loader
def _jwt_invalid(error: str):
    return jsonify(message="Invalid token"), 401


@jwt.expired_token_loader
def _jwt_expired(_jwt_header, jwt_payload):
    return jsonify(message="Token has expired"), 401
