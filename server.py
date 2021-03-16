from controllers.incidences.resource import incidences_controller
from controllers.municipalities.resource import municipalities_controller
from setup import app

app.register_blueprint(incidences_controller, url_prefix='/incidences')
app.register_blueprint(municipalities_controller, url_prefix='/municipalities')

# TODO: Implement generic error handler
# TODO: Config of settings/connection strings etc.

if __name__ == '__main__':
    app.run()
