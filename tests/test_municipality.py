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

    @staticmethod
    def get(bfs_nr) -> object:
        switcher = {
            3506: [{"area": 42.51, "bfsNr": 3506, "canton": "GR", "name": "Vaz/Obervaz", "population": 2780}],
            3544: [{"area": 190.14, "bfsNr": 3544, "canton": "GR", "name": "Berg\u00fcn Filisur", "population": 905}]
        }

        return switcher.get(int(bfs_nr), [])


@pytest.fixture
def service_mock(monkeypatch):
    def mock_get_all():
        return MockResponse().get_all()

    monkeypatch.setattr(MunicipalityService, 'get_all', mock_get_all)

    def mock_get(bfs_nr):
        return MockResponse().get(bfs_nr)

    monkeypatch.setattr(MunicipalityService, 'get', mock_get)


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
    data = response.get_json()
    assert len(data) == NUMBER_OF_MOCKED_MUNICIPALITIES


@pytest.mark.parametrize("bfsData", [[(42.51, 3506, "GR", "Vaz/Obervaz", 2780), (190.14, 3544, "GR", "Berg\u00fcn Filisur", 905)]])
def test_municipalities_base_all_data(client, app, service_mock, bfsData):
    """
    Check if /municipalities/ without filtering returns 
    the correct data
    """
    url = application_root+'/municipalities/'
    response = client.get(url)
    data = response.get_json()
    for i in range(0, NUMBER_OF_MOCKED_MUNICIPALITIES):
        assert (data[i]['area'], data[i]['bfsNr'], data[i]['canton'],
                data[i]['name'], data[i]['population']) in bfsData
    assert len(data) == len(bfsData)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_municipalities_filisur_request_statuscode_contenttype(client, app, service_mock):
    """
    Check if /municipalities/3544/ returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/municipalities/3544/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("bfsNr", [350, 35, 3])
def test_municipalities_bfsnr_not_found(client, app, service_mock, bfsNr):
    """
    Check if /municipalities/bfsNr/ returns 
    404 for not found bfsNr
    """
    url = application_root+'/municipalities/'+str(bfsNr)+'/'
    response = client.get(url)
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'No municipality found for bfsNr {str(bfsNr)}.'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()


@pytest.mark.parametrize("bfsNr", [35051, 350511, 3505262])
def test_municipalities_bfsnr_wrong_format(client, app, service_mock, bfsNr):
    """
    Check if /municipalities/bfsNr/ returns 
    invalid format message
    """
    url = application_root+'/municipalities/'+str(bfsNr)+'/'
    response = client.get(url)
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'Invalid format for parameter "bfsNr"'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()

@pytest.mark.parametrize("bfsNr", ["Scharans", "ABC", "35051"])
def test_municipalities_bfsnr_wrong_format_strings(client, app, service_mock, bfsNr):
    """
    Check if /municipalities/bfsNr/ returns 
    invalid format message
    """
    url = application_root+'/municipalities/'+str(bfsNr)+'/'
    response = client.get(url)
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'Invalid format for parameter "bfsNr"'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()


@pytest.mark.parametrize("bfsNr, bfsData", [(3506, (42.51, 3506, "GR", "Vaz/Obervaz", 2780)), (3544, (190.14, 3544, "GR", "Berg\u00fcn Filisur", 905))])
def test_municipalities_bfsnr_data(client, app, service_mock, bfsNr, bfsData):
    """
    Check if /municipalities/bfsNr/ returns 
    - the correct details (as of 01.01.2021) for the municipality "Bergün Filisur"
    """
    url = application_root+'/municipalities/'+str(bfsNr)+'/'
    response = client.get(url)
    data = response.get_json()[0]
    assert (data['area'], data['bfsNr'], data['canton'],
            data['name'], data['population']) in [bfsData]
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


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
    assert b'No municipality found for bfsNr 6621.' in response.get_data()
