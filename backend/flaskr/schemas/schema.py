from marshmallow import Schema, fields
from flaskr.schemas.plain_schema import (
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
