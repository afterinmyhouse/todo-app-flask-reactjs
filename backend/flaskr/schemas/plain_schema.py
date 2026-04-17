from marshmallow import Schema, fields, validate


class PlainUserSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainRegisterSchema(Schema):
    """Public self-registration body (same shape as user create, explicit name for OpenAPI)."""

    username = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1), load_only=True)


class PlainSignInSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class PlainTaskSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    status = fields.Str(
        validate=validate.OneOf(["PENDING", "IN_PROGRESS", "COMPLETED"]), required=True
    )
    created_at = fields.DateTime(dump_only=True, data_key="createdAt")


class PlainCreateProjectSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=60))
    description = fields.Str(load_default="", validate=validate.Length(max=280))


class PlainCreateTaskCommentSchema(Schema):
    """Body payload for POST /add-task-comment.

    ``taskId`` is the Mongo ObjectId of the task being commented on.
    ``body`` is the comment text, trimmed server-side; length validated
    before trimming to prevent a pathological all-whitespace 2000 char body.
    """

    task_id = fields.Str(required=True, data_key="taskId")
    body = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
