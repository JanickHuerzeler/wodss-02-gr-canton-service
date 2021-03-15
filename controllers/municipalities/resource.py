from flask import Blueprint

municipalities_controller = Blueprint('municipalities', __name__)

@municipalities_controller.route("/")
def get():
    return 'Hello Municipalities!'
