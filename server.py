from configManager import ConfigManager
from controllers.incidenceController import incidence_controller
from controllers.municipalityController import municipality_controller
from controllers.swaggerUIController import swaggerui_controller
from setup import app
import logging
from werkzeug.exceptions import InternalServerError, NotFound
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

server_config = ConfigManager.get_instance().get_server_config()
application_root = ConfigManager.get_instance().get_application_root()

app.register_blueprint(incidence_controller, url_prefix=application_root)
app.register_blueprint(municipality_controller, url_prefix=application_root)
app.register_blueprint(swaggerui_controller, url_prefix=application_root)


@app.errorhandler(Exception)
def handle_excpetion(e):
    if isinstance(e, NotFound):
        # Not found exception also contains automatic calls from browsers, e.g. to /favicon.ico
        logger.debug('A NotFound exception occurred.', exc_info=e)
        return e
    else:
        logger.critical('Unhandled Exception occurred', exc_info=e)
        return InternalServerError(description='An InternalServerError occurred. Please contact the administrator of this app.', original_exception=e)


if __name__ == '__main__':
    app.config['DEVELOPMENT'] = server_config["development"]
    app.run(debug=server_config["debug"],
            host=server_config["host"], port=server_config["port"])
