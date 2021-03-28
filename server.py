from configManager import ConfigManager
from controllers.incidenceController import incidence_controller
from controllers.municipalityController import municipality_controller
from setup import app

app.register_blueprint(incidence_controller)
app.register_blueprint(municipality_controller)

if __name__ == '__main__':
    server_config = ConfigManager.get_instance().get_server_config()

    app.config['DEVELOPMENT'] = server_config["development"]
    app.run(debug=server_config["debug"], host=server_config["host"], port=server_config["port"])
