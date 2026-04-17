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


class PlainTaskInProjectSchema(Schema):
    """A single initial task embedded inside a POST /add-project-with-tasks payload.

    Kept separate from ``PlainTaskSchema`` because this variant:

    * Does not require ``content`` (initial tasks often start as a title only).
    * Does not require ``tagId`` (tags are optional for this shortcut endpoint).
    * Defaults ``status`` to ``PENDING`` so the caller can omit it.
    """

    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(load_default="", validate=validate.Length(max=2000))
    status = fields.Str(
        load_default="PENDING",
        validate=validate.OneOf(["PENDING", "IN_PROGRESS", "COMPLETED"]),
    )
    tag_id = fields.Str(load_default=None, allow_none=True, data_key="tagId")


class PlainCreateProjectWithTasksSchema(Schema):
    """Top-level payload for POST /add-project-with-tasks.

    Bundles the project fields (same rules as /add-project) with an
    ``tasks`` array that must contain 1..50 items. The controller
    performs additional cross-field validation (e.g. rejecting
    duplicate task titles within the request).
    """

    name = fields.Str(required=True, validate=validate.Length(min=1, max=60))
    description = fields.Str(load_default="", validate=validate.Length(max=280))
    tasks = fields.List(
        fields.Nested(PlainTaskInProjectSchema),
        required=True,
        validate=validate.Length(min=1, max=50),
    )


class PlainCreateTaskCommentSchema(Schema):
    """Body payload for POST /add-task-comment.

    ``taskId`` is the Mongo ObjectId of the task being commented on.
    ``body`` is the comment text, trimmed server-side; length validated
    before trimming to prevent a pathological all-whitespace 2000 char body.
    """

    task_id = fields.Str(required=True, data_key="taskId")
    body = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
