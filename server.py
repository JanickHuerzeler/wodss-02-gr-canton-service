from configManager import ConfigManager
from controllers.incidences.resource import incidences_controller
from controllers.municipalities.resource import municipalities_controller
from setup import app

app.register_blueprint(incidences_controller, url_prefix='/incidences')
app.register_blueprint(municipalities_controller, url_prefix='/municipalities')

if __name__ == '__main__':
    server_config = ConfigManager.get_instance().get_server_config()

    app.config['DEVELOPMENT'] = server_config["development"]
    app.run(debug=server_config["debug"], host=server_config["host"], port=server_config["port"])
