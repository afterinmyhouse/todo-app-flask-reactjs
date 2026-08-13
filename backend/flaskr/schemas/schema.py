from marshmallow import Schema, fields
from flaskr.schemas.plain_schema import (
    PlainCreateProjectSchema,
    PlainCreateProjectWithTasksSchema,
    PlainCreateTaskCommentSchema,
    PlainRegisterSchema,
    PlainSignInSchema,
    PlainTagSchema,
    PlainTaskInProjectSchema,
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
    tag_name = fields.Str(dump_only=True, allow_none=True, data_key="tagName")
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


class CreateTaskCommentSchema(PlainCreateTaskCommentSchema):
    """Payload for creating a task comment."""


class TaskCommentSchema(Schema):
    id = fields.Str(required=True)
    task_id = fields.Str(required=True, data_key="taskId")
    body = fields.Str(required=True)
    created_at = fields.DateTime(required=True, data_key="createdAt")


class CreateProjectWithTasksSchema(PlainCreateProjectWithTasksSchema):
    """Payload for creating a project together with its initial tasks."""


class TaskInProjectResponseSchema(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    status = fields.Str(required=True)
    tag_name = fields.Str(required=False, allow_none=True, data_key="tagName")
    created_at = fields.DateTime(required=True, data_key="createdAt")


class ProjectWithTasksSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(required=True, data_key="createdAt")
    tasks = fields.List(fields.Nested(TaskInProjectResponseSchema), required=True)


# --- GET /search (workspace entity search) ---------------------------------


class SearchTagHitSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)


class SearchTaskHitSchema(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    status = fields.Str(required=True)
    tag_name = fields.Str(required=False, allow_none=True, data_key="tagName")
    snippet = fields.Str(
        required=False,
        metadata={"description": "Short excerpt from task content for context"},
    )


class SearchProjectHitSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)


class SearchResultsBucketSchema(Schema):
    tags = fields.List(fields.Nested(SearchTagHitSchema), required=True)
    tasks = fields.List(fields.Nested(SearchTaskHitSchema), required=True)
    projects = fields.List(fields.Nested(SearchProjectHitSchema), required=True)


class SearchResponseSchema(Schema):
    query = fields.Str(required=True)
    results = fields.Nested(SearchResultsBucketSchema, required=True)
