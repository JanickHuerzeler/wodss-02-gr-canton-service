from flask import Blueprint

incidences_controller = Blueprint('incidences', __name__)

@incidences_controller.route("/")
def get():
    return 'Hello Incidences!'
