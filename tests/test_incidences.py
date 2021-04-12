import pytest
from flask import json, jsonify
from configManager import ConfigManager
from services.IncidenceService import IncidenceService
from models.incidence import Incidence
application_root = ConfigManager.get_instance().get_application_root()




# db.session.query(Incidence) müsste hier gemockt werden, damit .filter trotzdem noch getestet wird. 

def test_incidences_base_route(client, app):
    """
    Check if /incidences/ route returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/incidences/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

def test_incidences_for_one_day(client, app):
    """
    Check if /incidences/?dateFrom=2020-02-28&dateTo=2020-02-28 returns 
    - a list of all 100 municipalities of the canton GR
    - each municipalitiy list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date equals 2020-02-28
    - each bfsNr is given
    - each incidence is given
    """
    url = application_root+'/incidences/?dateFrom=2020-02-28&dateTo=2020-02-28'
    response = client.get(url)
    data = response.get_json()
    assert len(data) == 101
    for i in range(0,101):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] == '2020-02-28'
        assert data[i]['incidence'] is not None

def test_municipalities_dateTo_smaller_than_dateFrom(client, app):
    """
    Check if /incidences/?dateFrom=2020-02-28&dateTo=2020-02-27 returns 
    - 404 status code
    - correct content-type
    """
    url = application_root+'/incidences/?dateFrom=2020-02-28&dateTo=2020-02-27'
    response = client.get(url)
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo))' in response.get_data()
