from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from flaskr.controllers.search_controller import SearchController
from flaskr.schemas.schema import SearchResponseSchema

bp = Blueprint("search", __name__)


@bp.route("/search")
class WorkspaceSearch(MethodView):
    @jwt_required()
    @bp.response(200, SearchResponseSchema)
    def get(self):
        """Search the signed-in user's tasks & projects and global tags by substring."""
        q = request.args.get("q", "")
        return SearchController.search(q)
