from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

from configManager import ConfigManager

swaggerui_controller = Blueprint('swaggerui_controller', __name__)

application_root = ConfigManager.get_instance().get_application_root()
SWAGGER_URL = '/v1'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API url

# Call factory function to create our blueprint
swaggerui_controller = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL
)
