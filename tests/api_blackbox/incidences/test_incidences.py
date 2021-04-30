import pytest
from flask import json, jsonify
from configManager import ConfigManager
from services.incidence_service import IncidenceService
from models.incidence import Incidence
from datetime import datetime, timedelta
application_root = ConfigManager.get_instance().get_application_root()


NUMBER_OF_MUNICIPALITIES_IN_GR = 101
DAYS_OF_MEASURES_IN_TEST_DATA_SET = 411
''' 
This Test file makes use of a mocked db with static SQL Data.
- dump_incidences.sql
- dump_municipalities.sql
'''


'''
Tests for /incidences/ with and without dateFrom & dateTo Filters
'''


def test_incidences_base_route(client, app):
    """
    Check if /incidences/ route returns 
    - correct content-type "application/json"
    - status code 200
    """
    # Given
    url = application_root+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_incidences_without_datefrom_dateto_params(client, app):
    """
    Check if /incidences/ returns 
    - a list of all NUMBER_OF_MUNICIPALITIES_IN_GR municipalities of the canton GR
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date equals the current date
    - each bfsNr is given
    - each incidence is given
    """
    # Given
    url = application_root+'/incidences/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert len(data) == NUMBER_OF_MUNICIPALITIES_IN_GR * \
        DAYS_OF_MEASURES_IN_TEST_DATA_SET
    for i in range(0, NUMBER_OF_MUNICIPALITIES_IN_GR*DAYS_OF_MEASURES_IN_TEST_DATA_SET):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None


@pytest.mark.parametrize("test_date", ['2020-02-28', '2020-08-31', '2020-11-30', '2021-03-31'])
def test_incidences_for_one_day(client, app, test_date):
    """
    Check if /incidences/?dateFrom=test_date&dateTo=test_date returns 
    - a list of all NUMBER_OF_MUNICIPALITIES_IN_GR municipalities of the canton GR
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date equals test_date
    - each bfsNr is given
    - each incidence is given
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+test_date+'&dateTo='+test_date

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert len(data) == NUMBER_OF_MUNICIPALITIES_IN_GR
    for i in range(0, NUMBER_OF_MUNICIPALITIES_IN_GR):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] == test_date
        assert data[i]['incidence'] is not None


@pytest.mark.parametrize("dateFrom", ['2021-04-12'])
def test_incidences_for_current_date_empty(client, app, dateFrom):
    """
    Check if dateFrom=Future Date (2021-04-11 as last measure date of test data set) returns 
    - an empty list
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+dateFrom+''

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert data == []
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("dateFrom", [(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')])
def test_incidences_for_future_datefrom_with_default_dateto_fallback_today(client, app, dateFrom):
    """
    When providing a dateFrom in the future and not providing a dateTo,
    by default dateTo gets set to today's date. Therefore we should get
    a 400 response due to invalid date condition (dateFrom <= dateTo).
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+dateFrom+''

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo))' in response.get_data(
    )


@pytest.mark.parametrize("dateTo", ['2020-02-26'])
def test_incidences_for_given_date_to_with_default_datefrom_fallback(client, app, dateTo):
    """
    When providing a dateFrom in the future and not providing a dateTo,
    by default dateTo gets set to today's date. Therefore we should get
    a 400 response due to invalid date condition (dateFrom <= dateTo).
    """
    # Given
    url = application_root+'/incidences/?dateTo='+dateTo+''

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    data = response.get_json()
    assert len(data) == NUMBER_OF_MUNICIPALITIES_IN_GR
    for i in range(0, NUMBER_OF_MUNICIPALITIES_IN_GR):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] == dateTo
        assert data[i]['incidence'] is not None


@pytest.mark.parametrize("dateFrom, dateTo", [('2020-02-28', '2020-02-27'), ('2021-02-14', '2021-02-13')])
def test_incidences_datefrom_bigger_than_dateTo(client, app, dateFrom, dateTo):
    """
    Check if we get a 400 status code for /incidences/ if dateFrom is bigger than dateTo
    - 400 status code
    - correct content-type
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo))' in response.get_data(
    )


@pytest.mark.parametrize("dateFrom, dateTo", [('2021-04-14', '2021-04-14'), ('2021-04-14', '2021-06-14')])
def test_incidences_for_future_day_ranges(client, app, dateFrom, dateTo):
    """
    Check if we get an OK status code (200) and empty responses for valid,
    but future date ranges for which no data exists yet.
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert data == []
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("dateFrom, dateTo, dayDiff", [('2021-02-14', '2021-02-14', 1), ('2021-02-12', '2021-02-14', 3)])
def test_incidences_for_one_day(client, app, dateFrom, dateTo, dayDiff):
    """
    Check if /incidences/?dateFrom=[dateFrom]&dateTo=[dateTo] returns 
    - a list of all NUMBER_OF_MUNICIPALITIES_IN_GR municipalities of the canton GR
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date equals test_date
    - each bfsNr is given
    - each incidence is given
    """
    # Given
    url = application_root+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == NUMBER_OF_MUNICIPALITIES_IN_GR*dayDiff
    for i in range(0, NUMBER_OF_MUNICIPALITIES_IN_GR*dayDiff):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


'''
Tests for /incidences/bfsNr/

'''


@pytest.mark.parametrize("dateFrom, dateTo, dayDiff, bfsNr, dateIncidences", [
    ('2021-02-14', '2021-02-14', 1, 3506, [('2021-02-14', 35.97122302158274)]),
    ('2021-01-20', '2021-01-21', 2, 3506,
     [('2021-01-20', 143.88489208633095), ('2021-01-21', 107.9136690647482)]),
    ('2020-10-25', '2020-10-30', 6, 3543, [
        ('2020-10-25', 297.11375212224107),
        ('2020-10-26', 339.5585738539898),
        ('2020-10-27', 339.5585738539898),
        ('2020-10-28', 424.44821731748726),
        ('2020-10-29', 466.893039049236),
        ('2020-10-30', 551.7826825127335)
    ])
])
def test_incidences_bfsNr(client, app, dateFrom, dateTo, dayDiff, bfsNr, dateIncidences):
    """
    Check if /incidences/bfsNr?dateFrom=dateFrom&dateTo=dateTo returns 
    - a list of all incidence data items for the given bfsNr
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date equals is between dateFrom and dateTo
    - each bfsNr is given
    - each incidence is given
    """
    # Given
    url = application_root+'/incidences/' + \
        str(bfsNr)+'/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    for i in range(0, dayDiff):
        assert data[i]['bfsNr'] == bfsNr
        assert (data[i]['date'], round(data[i]['incidence'], 12)) in [
            (date, round(incidence, 12)) for date, incidence in dateIncidences]


@pytest.mark.parametrize("dateFrom, dateTo, dayDiff, bfsNr, dateIncidences", [
    ('2021-02-15', '2021-02-14', 1, 3506, [('2021-02-14', 35.97122302158274)]),
    ('2021-01-25', '2021-01-21', 2, 3506,
     [('2021-01-20', 143.88489208633095), ('2021-01-21', 107.9136690647482)]),
    ('2020-10-31', '2020-10-30', 6, 3543, [
        ('2020-10-25', 297.11375212224107),
        ('2020-10-26', 339.5585738539898),
        ('2020-10-27', 339.5585738539898),
        ('2020-10-28', 424.44821731748726),
        ('2020-10-29', 466.893039049236),
        ('2020-10-30', 551.7826825127335)
    ])
])
def test_incidences_bfsnr_datefrom_bigger_than_dateto(client, app, dateFrom, dateTo, dayDiff, bfsNr, dateIncidences):
    """
    Check if /incidences/bfsNr?dateFrom=dateFrom&dateTo=dateTo returns 
    a 400 status code and according message if dateFrom is bigger than dateTo
    """
    # Given
    url = application_root+'/incidences/' + \
        str(bfsNr)+'/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo))' in response.get_data(
    )


@pytest.mark.parametrize("dateFrom, dateTo, dayDiff, bfsNr", [
    ('2022-05-15', '2022-05-15', 1, 3506),
    ('2022-05-25', '2022-05-26', 2, 3506),
    ('2022-05-30', '2022-06-05', 6, 3543)
])
def test_incidences_bfsnr_future_date_ranges(client, app, dateFrom, dateTo, dayDiff, bfsNr):
    """
    Check if /incidences/bfsNr?dateFrom=dateFrom&dateTo=dateTo with dates in the future return 200 with empty array
    """
    # Given
    url = application_root+'/incidences/' + \
        str(bfsNr)+'/?dateFrom='+dateFrom+'&dateTo='+dateTo+''

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    data = response.get_json()
    assert len(data) == 0


@pytest.mark.parametrize("bfsNr", [350, 35, 3])
def test_incidences_bfsnr_not_found(client, app, bfsNr):
    """
    Check if /incidences/bfsNr/ returns 
    404 for not found bfsNr
    """
    # Given
    url = application_root+'/incidences/'+str(bfsNr)+'/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'No municipality found for bfsNr {bfsNr}.'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()


@pytest.mark.parametrize("bfsNr", [35051, 350511, 3505262])
def test_incidences_bfsnr_wrong_format(client, app, bfsNr):
    """
    Check if /municipalities/bfsNr/ returns 
    invalid format message
    """
    # Given
    url = application_root+'/incidences/'+str(bfsNr)+'/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'Invalid format for parameter "bfsNr"'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()


@pytest.mark.parametrize("bfsNr", ["Scharans", "ABC", "35051"])
def test_incidences_bfsnr_wrong_format_strings(client, app, bfsNr):
    """
    Check if /municipalities/bfsNr/ returns 
    invalid format message
    """
    # Given
    url = application_root+'/incidences/'+str(bfsNr)+'/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expectedMessage = f'Invalid format for parameter "bfsNr"'
    assert bytes(expectedMessage, encoding='utf8') in response.get_data()
