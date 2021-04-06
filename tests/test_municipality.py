import pytest
from flask import json, jsonify
from configManager import ConfigManager

application_root = ConfigManager.get_instance().get_application_root()


def test_municipalities_base_route(client, app):
    """
    Check if /municipalities/ route returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/municipalities/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

def test_municipalities_base_route(client, app):
    """
    Check if /municipalities/ without filtering returns 
    - a list of all 100 municipalities of the canton GR
    - current dates
    """
    url = application_root+'/municipalities/'
    response = client.get(url)
    data = response.get_json()
    assert len(data) == 100

def test_municipalities_filisur_request(client, app):
    """
    Check if /municipalities/3544/ returns 
    - correct content-type "application/json"
    - status code 200
    """
    url = application_root+'/municipalities/3544/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_municipalities_filisur_data(client, app):
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

def test_municipalities_inexistent_bfsNr(client, app):
    """
    Check if /municipalities/6621/ (Geneva) returns 
    - 404 status code
    - correct content-type
    """
    url = application_root+'/municipalities/6621/'
    response = client.get(url)
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"


def test_municipalities_inexistent_bfsNr(client, app):
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
