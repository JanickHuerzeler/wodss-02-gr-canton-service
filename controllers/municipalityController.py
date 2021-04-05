from flask import jsonify, Blueprint

from services.MunicipalityService import MunicipalityService
from services.ErrorHandlerService import ErrorHandlerService

municipality_controller = Blueprint('municipality_controller', __name__, template_folder='templates')


@municipality_controller.route("/municipalities/", methods=['GET'])
def get_all():
    municipalities = MunicipalityService.get_all()
    return jsonify(municipalities)


@municipality_controller.route("/municipalities/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfs_nr):
        return 'Invalid format for parameter "bfsNr"', 400

    municipalities = MunicipalityService.get(bfs_nr)

    if municipalities:
        return jsonify(municipalities)
    else:
        return 'No municipality found for bfsNr ' + bfs_nr + '!', 404
