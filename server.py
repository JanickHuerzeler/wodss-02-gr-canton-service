from configManager import ConfigManager
from controllers.incidenceController import incidence_controller
from controllers.municipalityController import municipality_controller
from controllers.swaggerUIController import swaggerui_controller
from setup import app

server_config = ConfigManager.get_instance().get_server_config()
application_root = ConfigManager.get_instance().get_application_root()

app.register_blueprint(incidence_controller, url_prefix=application_root)
app.register_blueprint(municipality_controller, url_prefix=application_root)


if __name__ == '__main__':
    app.config['DEVELOPMENT'] = server_config["development"]
    app.run(debug=server_config["debug"], host=server_config["host"], port=server_config["port"])
