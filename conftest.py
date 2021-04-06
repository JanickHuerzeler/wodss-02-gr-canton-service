from setup import create_app

import pytest


from configManager import ConfigManager
from controllers.incidenceController import incidence_controller
from controllers.municipalityController import municipality_controller
from controllers.swaggerUIController import swaggerui_controller
from setup import app


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():

        server_config = ConfigManager.get_instance().get_server_config()
        application_root = ConfigManager.get_instance().get_application_root()

        app.register_blueprint(incidence_controller, url_prefix=application_root)
        app.register_blueprint(municipality_controller, url_prefix=application_root)
        app.register_blueprint(swaggerui_controller, url_prefix=application_root)

        app.config['DEVELOPMENT'] = server_config["development"]
        # app.run(debug=server_config["debug"], host=server_config["host"], port=server_config["port"])
        yield app

# https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/tests/conftest.py
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/tests/conftest.py
@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()