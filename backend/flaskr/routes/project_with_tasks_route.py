from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from flaskr.controllers.project_with_tasks_controller import ProjectWithTasksController
from flaskr.schemas.schema import CreateProjectWithTasksSchema, ProjectWithTasksSchema

bp = Blueprint("project_with_tasks", __name__)


@bp.route("/add-project-with-tasks")
class AddProjectWithTasks(MethodView):
    @jwt_required()
    @bp.arguments(CreateProjectWithTasksSchema)
    @bp.response(201, ProjectWithTasksSchema)
    def post(self, data):
        """Create a project together with 1..50 initial tasks (JWT required)."""
        return ProjectWithTasksController.create(data)
