import pytest
from flask import json, jsonify

def test_municipalities_base_route(client, app):
    url = '/municipalities/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

def test_municipalities_base_route(client, app):
    url = '/municipalities/'
    response = client.get(url)
    data = response.get_json()
    assert len(data) == 100

def test_municipalities_filisur_request(client, app):
    url = '/municipalities/3544/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

def test_municipalities_filisur_data(client, app):
    url = '/municipalities/3544/'
    response = client.get(url)
    data = response.get_json()[0]
    assert data["area"] == 190.14
    assert data["bfsNr"] == 3544
    assert data["canton"] == 'GR'
    assert data["name"] == 'Bergün Filisur'
    assert data["population"] == 905
    