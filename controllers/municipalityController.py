from flask import jsonify, Blueprint
import logging

from services.MunicipalityService import MunicipalityService
from services.ErrorHandlerService import ErrorHandlerService

logger = logging.getLogger(__name__)

municipality_controller = Blueprint(
    'municipality_controller', __name__, template_folder='templates')


@municipality_controller.route("/municipalities/", methods=['GET'])
def get_all():
    logger.info(
        f'GET /municipalities/ was called.')

    municipalities = MunicipalityService.get_all()
    return jsonify(municipalities)


@municipality_controller.route("/municipalities/<bfs_nr>/", methods=['GET'])
def get(bfs_nr):

    logger.info(
        f'GET /municipalities/<bfs_nr>/ was called. (bfs_nr: {bfs_nr}')

    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfs_nr):
        error_message = 'Invalid format for parameter "bfsNr"'
        logger.debug(f'{error_message}. (bfs_nr: {bfs_nr})')
        return error_message, 400

    municipalities = MunicipalityService.get(bfs_nr)

    if municipalities:
        return jsonify(municipalities)
    else:
        error_message = f'No municipality found for bfsNr {bfs_nr}!'
        logger.debug(error_message)
        return error_message, 404
