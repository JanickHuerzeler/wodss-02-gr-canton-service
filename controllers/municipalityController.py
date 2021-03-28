from flask import jsonify, Blueprint
from services.MunicipalityService import MunicipalityService

municipality_controller = Blueprint('municipality_controller', __name__)


@municipality_controller.route("/municipalities/", methods=['GET'])
def get_all():
    #TODO: Validation and Errorhandling

    municipalities = MunicipalityService.get_all()
    return jsonify(municipalities)


@municipality_controller.route("/municipalities/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    #TODO: Validation and Errorhandling

    municipalities = MunicipalityService.get(bfs_nr)

    if municipalities:
        return jsonify(municipalities)
    else:
        return 'No municipality found for bfsNr ' + bfs_nr + '!', 404
