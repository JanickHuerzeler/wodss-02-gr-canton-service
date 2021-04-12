from models.municipality import Municipality
from typing import List
from services.MunicipalityService import MunicipalityService
import pytest
from flask import json, jsonify
from configManager import ConfigManager

application_root = ConfigManager.get_instance().get_application_root()


NUMBER_OF_MOCKED_MUNICIPALITIES = 2


class MockResponse:
    @staticmethod
    def get_all() -> List[Municipality]:
        return [{"area": 42.51, "bfsNr": 3506, "canton": "GR", "name": "Vaz/Obervaz", "population": 2780},
                {"area": 190.14, "bfsNr": 3544, "canton": "GR", "name": "Berg\u00fcn Filisur", "population": 905}]


@pytest.fixture
def service_mock(monkeypatch):
    def mock_get_all():
        return MockResponse().get_all()

    monkeypatch.setattr(MunicipalityService, 'get_all', mock_get_all)


def test_municipalities_base_route(client, app, service_mock):
    """
    Check if /municipalities/ route returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/municipalities/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_municipalities_base_route(client, app, service_mock):
    """
    Check if /municipalities/ without filtering returns 
    - a list of all 100 municipalities of the canton GR
    - current dates
    """
    url = application_root+'/municipalities/'
    response = client.get(url)
    data = response.get_json()
    assert len(data) == NUMBER_OF_MOCKED_MUNICIPALITIES


def test_municipalities_filisur_request(client, app, service_mock):
    """
    Check if /municipalities/3544/ returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/municipalities/3544/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_municipalities_filisur_data(client, app, service_mock):
    """
    Check if /municipalities/3544/ returns 
    - the correct details (as of 01.01.2021) for the municipality "Bergün Filisur"
    """
    url = application_root+'/municipalities/3544/'
    response = client.get(url)
    data = response.get_json()[0]
    assert data["area"] == 190.14
    assert data["bfsNr"] == 3544
    assert data["canton"] == 'GR'
    assert data["name"] == 'Bergün Filisur'
    assert data["population"] == 905


def test_municipalities_inexistent_bfsNr(client, app, service_mock):
    """
    Check if /municipalities/6621/ (Geneva) returns 
    - 404 status code
    - correct content-type
    """
    url = application_root+'/municipalities/6621/'
    response = client.get(url)
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"


def test_municipalities_inexistent_bfsNr(client, app, service_mock):
    """
    Check if /municipalities/6621/ (Geneva) returns 
    - 404 status code
    - correct content-type
    """
    url = application_root+'/municipalities/6621/'
    response = client.get(url)
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'No municipality found for bfsNr 6621!' in response.get_data()


# TODO /Municipality/bfsNr: Format Korrekt/inkorrekt abdecken
# TODO /Municipality/bfsNr: Format nichtvorhandene bfsNr abdecken
# TODO /Municipality/bfsNr: Format vorhandene bfsNr abdecken


def test_municipalities_get_all(client, service_mock):
    url = application_root+'/municipalities/'
    response = client.get(url)
    print(response)
    data = response.get_json()[0]
    assert response.status_code == 200
    assert data["area"] == 42.51
    assert data["bfsNr"] == 3506
    assert data["canton"] == 'GR'
    assert data["name"] == 'Vaz/Obervaz'
    assert data["population"] == 2780


# from unittest.mock import Mock, patch
# from services.MunicipalityService import MunicipalityService
# @pytest.fixture
# def mock_ms_get_all():
#     return Mock(spec=MunicipalityService)
# def test_municipalities_get_all(client, mock_ms_get_all):
#     municipalities = [{
#       "area": 42.51,
#       "bfsNr": 3506,
#       "canton": "GR",
#       "name": "Vaz/Obervaz",
#       "population": 2780
#     },{
#       "area": 11.35,
#       "bfsNr": 3514,
#       "canton": "GR",
#       "name": "Schmitten (GR)",
#       "population": 234
#     }]

#     mock_ms_get_all = Mock(name='MunicipalityService.get_all Mock', return_value = municipalities)
#     MunicipalityService.get_all = mock_ms_get_all

#     # mock_ms_get_all.get_all.return_value = municipalities
#     url = application_root+'/municipalities/'
#     response = client.get(url)
#     assert response.status_code == 200
#     mock_ms_get_all.assert_called_once()
#     data = response.get_json()[0]

#     assert data["area"] == 42.51
#     assert data["bfsNr"] == 3506
#     assert data["canton"] == 'GR'
#     assert data["name"] == 'Vaz/Obervaz'
#     assert data["population"] == 2780

#     data = response.get_json()[1]
#     assert data["area"] == 11.35
#     assert data["bfsNr"] == 3514
#     assert data["canton"] == 'GR'
#     assert data["name"] == 'Schmitten (GR)'
#     assert data["population"] == 234
