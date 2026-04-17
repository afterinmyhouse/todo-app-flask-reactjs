from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from flaskr.controllers.task_comment_controller import TaskCommentController
from flaskr.schemas.schema import CreateTaskCommentSchema, TaskCommentSchema

bp = Blueprint("task_comments", __name__)


@bp.route("/add-task-comment")
class AddTaskComment(MethodView):
    @jwt_required()
    @bp.arguments(CreateTaskCommentSchema)
    @bp.response(201, TaskCommentSchema)
    def post(self, data):
        """Create a comment on a task owned by the caller (JWT required)."""
        return TaskCommentController.create(data)
