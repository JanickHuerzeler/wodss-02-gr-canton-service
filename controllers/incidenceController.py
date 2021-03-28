from datetime import datetime
from flask import jsonify, request, Blueprint
from services.IncidenceService import IncidenceService
from services.ErrorHandlerService import ErrorHandlerService
from configManager import ConfigManager

incidence_controller = Blueprint('incidence_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()


@incidence_controller.route("/incidences/", methods=['GET'])
def get_all():
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today().strftime(df)

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return 'Invalid format for parameter "dateFrom" (required: ' + df + ')', 400
    if not ErrorHandlerService.check_date_format(date_to):
        return 'Invalid format for parameter "dateTo" (required: ' + df + ')', 400
    if not ErrorHandlerService.check_date_sematic(date_from, date_to):
        return 'Invalid semantic in dates (required: dateFrom <= dateTo))', 400

    incidences = IncidenceService.get_all(date_from, date_to)
    return jsonify(incidences)


@incidence_controller.route("/incidences/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today().strftime(df)

    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfs_nr):
        return 'Invalid format for parameter "bfsNr" (required: 4-digit number)', 400

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return 'Invalid format for parameter "dateFrom" (required: ' + df + ')', 400
    if not ErrorHandlerService.check_date_format(date_to):
        return 'Invalid format for parameter "dateTo" (required: ' + df + ')', 400
    if not ErrorHandlerService.check_date_sematic(date_from, date_to):
        return 'Invalid semantic in dates (required: dateFrom <= dateTo))', 400

    incidences = IncidenceService.get(bfs_nr, date_from, date_to)

    if incidences:
        return jsonify(incidences)
    else:
        return 'No incidences found for bfsNr ' + bfs_nr + '!', 404
