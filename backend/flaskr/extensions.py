from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

api = Api()
cors = CORS()
jwt = JWTManager()
