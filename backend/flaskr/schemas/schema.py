from marshmallow import Schema, fields
from flaskr.schemas.plain_schema import (
    PlainCreateProjectSchema,
    PlainRegisterSchema,
    PlainSignInSchema,
    PlainTagSchema,
    PlainTaskSchema,
    PlainUserSchema,
)


class UserSchema(PlainUserSchema):
    pass


class SignInSchema(PlainSignInSchema):
    pass


class LoginSchema(PlainSignInSchema):
    """Credentials for POST /auth/login (same shape as legacy sign-in)."""


class LoginResponseSchema(Schema):
    """JWT access token for Authorization: Bearer <token>. Expiry set server-side (see JWT_ACCESS_TOKEN_EXPIRES)."""

    token = fields.Str(required=True, metadata={"description": "JWT access token"})


class RegisterSchema(PlainRegisterSchema):
    pass


class RegisterResponseSchema(Schema):
    """Returned after successful registration (user record + JWT for immediate session)."""

    id = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    token = fields.Str(required=True)


class TagSchema(PlainTagSchema):
    pass


class TaskSchema(PlainTaskSchema):
    tag_name = fields.Str(dump_only=True, data_key="tagName")
    tag_id = fields.Str(required=True, load_only=True, data_key="tagId")


class UpdateTaskSchema(PlainTaskSchema):
    pass


class CreateProjectSchema(PlainCreateProjectSchema):
    """Payload for creating a project."""


class ProjectSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(required=True, data_key="createdAt")
