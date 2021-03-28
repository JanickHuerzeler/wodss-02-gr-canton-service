from datetime import datetime
from flask import jsonify, request, Blueprint
from services.IncidenceService import IncidenceService

incidence_controller = Blueprint('incidence_controller', __name__)


@incidence_controller.route("/incidences/", methods=['GET'])
def get_all():
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(0)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today()

    #TODO: Validation and Errorhandling

    incidences = IncidenceService.get_all(date_from, date_to)
    return jsonify(incidences)


@incidence_controller.route("/incidences/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(0)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today()

    #TODO: Validation and Errorhandling

    incidences = IncidenceService.get(bfs_nr, date_from, date_to)

    if incidences:
        return jsonify(incidences)
    else:
        return 'No incidences found for bfsNr ' + bfs_nr + '!', 404
