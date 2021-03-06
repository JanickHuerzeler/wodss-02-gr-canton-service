from datetime import datetime
from flask import jsonify, request, Blueprint
from services.incidence_service import IncidenceService
from services.municipality_service import MunicipalityService
from services.errorhandler_service import ErrorHandlerService
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
import logging

logger = logging.getLogger(__name__)

incidence_controller = Blueprint('incidence_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()


@incidence_controller.route("/incidences/", methods=['GET'])
def get_all():
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(
        0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today(
    ).strftime(df)

    logger.info(
        f'GET /incidences/ was called. (date_from: {date_from}, date_to: {date_to})')

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return date_bad_request(f'Invalid format for parameter "dateFrom" (required: {df})', None, date_from, None)
    if not ErrorHandlerService.check_date_format(date_to):
        return date_bad_request(f'Invalid format for parameter "dateTo" (required: {df})', None, None, date_to)
    if not ErrorHandlerService.check_date_semantic(date_from, date_to):
        return date_bad_request('Invalid semantic in dates (required: dateFrom <= dateTo))', None, date_from, date_to)

    incidences = IncidenceService.get_all(date_from, date_to)

    logger.debug(
        f'Found {len(incidences)} incidences. (date_from: {date_from}, date_to: {date_to})')

    return jsonify(incidences)


@incidence_controller.route("/incidences/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(
        0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today(
    ).strftime(df)

    logger.info(
        f'GET /incidences/<bfs_nr>/ was called. (bfs_nr: {bfs_nr}, date_from: {date_from}, date_to: {date_to})')

    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfs_nr):
        return bfs_nr_bad_request('Invalid format for parameter "bfsNr" (required: 4-digit number)', bfs_nr)

    # Check if municipality exists for given bfs_nr
    municipality = MunicipalityService.get(bfs_nr)
    if not municipality:
        error_message = f'No municipality found for bfsNr {bfs_nr}.'
        logger.debug(error_message)
        return error_message, 404

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return date_bad_request(f'Invalid format for parameter "dateFrom" (required: {df})', bfs_nr, date_from, None)
    if not ErrorHandlerService.check_date_format(date_to):
        return date_bad_request(f'Invalid format for parameter "dateTo" (required: {df})', bfs_nr, None, date_to)
    if not ErrorHandlerService.check_date_semantic(date_from, date_to):
        return date_bad_request('Invalid semantic in dates (required: dateFrom <= dateTo))', bfs_nr, date_from, date_to)

    incidences = IncidenceService.get(bfs_nr, date_from, date_to)

    logger.debug(
        f'Found {len(incidences)} incidences for given bfsNr. (bfsNr: {bfs_nr}, date_from: {date_from}, date_to: {date_to})')
    return jsonify(incidences)


def bfs_nr_bad_request(error_message, bfs_nr):
    logger.debug(f'{error_message}. (bfs_nr: {bfs_nr})')
    return error_message, 400


def date_bad_request(error_message, bfs_nr, date_from, date_to):
    params = (f'bfs_nr: {bfs_nr}, ' if bfs_nr else '') + \
        (f'date_from: {date_from}, ' if date_from else '') + \
        (f'date_to: {date_to}), ' if date_to else '')

    params = params[:-2] if params.endswith(', ') else params

    logger.debug(f'{error_message}. ({params})')
    return error_message, 400
