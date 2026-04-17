from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from flaskr.controllers.project_controller import ProjectController
from flaskr.schemas.schema import CreateProjectSchema, ProjectSchema

bp = Blueprint("projects", __name__)


@bp.route("/add-project")
class AddProject(MethodView):
    @jwt_required()
    @bp.arguments(CreateProjectSchema)
    @bp.response(201, ProjectSchema)
    def post(self, data):
        """Protected route (JWT Required)"""
        return ProjectController.create(data)
