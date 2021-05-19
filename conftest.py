from app import get_test_app, db
from sqlalchemy.sql import text
import pytest

from configManager import ConfigManager
from controllers.incidence_controller import incidence_controller
from controllers.municipality_controller import municipality_controller
from controllers.swaggerui_controller import swaggerui_controller
from app import app

@pytest.fixture
def app():
    app = get_test_app()

    with app.app_context():

        server_config = ConfigManager.get_instance().get_server_config()
        application_root = ConfigManager.get_instance().get_application_root()

        app.register_blueprint(incidence_controller, url_prefix=application_root)
        app.register_blueprint(municipality_controller, url_prefix=application_root)
        app.register_blueprint(swaggerui_controller, url_prefix=application_root)

        app.config['DEVELOPMENT'] = server_config["development"]

        with app.open_resource("tests/api_blackbox/testdata/dump_municipalities.sql") as f_municipalities:
            with app.open_resource("tests/api_blackbox/testdata/dump_incidences.sql") as f_incidences:
                engine = db.get_engine()

                with engine.connect() as con:

                    create_incidence = '''
                    CREATE TABLE incidence (
                        "incidencesId" integer NOT NULL,
                        "bfsNr" integer NOT NULL,
                        date date NOT NULL,
                        incidence double precision NOT NULL,
                        cases integer NOT NULL,
                        cases_cumsum_14d integer NOT NULL
                    );
                    '''

                    create_municipality = '''
                    CREATE TABLE municipality (
                        "bfsNr" integer NOT NULL,
                        name character varying(256) NOT NULL,
                        canton character varying(2) NOT NULL,
                        area double precision NOT NULL,
                        population integer NOT NULL,
                        region character varying(256) NOT NULL
                    );
                    '''

                    con.execute(create_municipality)
                    con.execute(create_incidence)

                    query_municipalities = text(f_municipalities.read().decode("utf8"))
                    con.execute(query_municipalities)
                    query_incidences = text(f_incidences.read().decode("utf8"))
                    con.execute(query_incidences)

        yield app

# Source: https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/tests/conftest.py
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# Source: https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/tests/conftest.py
@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
