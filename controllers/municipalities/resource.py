from flask import jsonify, Blueprint
from services.MunicipalityService import MunicipalityService

municipalities_controller = Blueprint('municipalities', __name__)


@municipalities_controller.route("/", methods=['GET'])
def get_all():
    #TODO: Validation and Errorhandling

    municipalities = MunicipalityService.get_all()
    return jsonify(municipalities)


@municipalities_controller.route("/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    #TODO: Validation and Errorhandling

    municipalities = MunicipalityService.get(bfs_nr)

    if municipalities:
        return jsonify(municipalities)
    else:
        return 'No municipality found for bfsNr ' + bfs_nr + '!', 404
