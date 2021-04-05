import requests
import json
import pandas as pd
import time
from datetime import datetime, timedelta

# The covid-19 API allows only sending 2000 data rows per request
# One date contains 12 rows. Thererfore we can request up to 166 days per request (166 * 12 = 1992)
MAX_DAYS_PER_REQUEST = 166
MAX_RESULT_ROWS = 1992


def fetch_corona_data(dateFrom, dateTo) -> str:
    ''' 
    Performs a query on the canton endpoint for receiving covid-19 data. See https://curl.trillworks.com/ for request usage.
    '''
    endpointUrl = 'https://services1.arcgis.com/YAuo6vcW85VPu7OE/ArcGIS/rest/services/Fallzahlen_Pro_Region/FeatureServer/0/query'

    # params = (
    # ('f', 'json'),
    # ('limit', f'{limit}'),
    # ('offset', f'{offset}'),
    # ('where', '1=1'),
    # ('objectIds',''),
    # ('time',''),
    # ('resultType','none'),
    # ('outFields', '*'),
    # ('returnIdsOnly','false'),
    # ('returnUniqueIdsOnly','false'),
    # ('returnCountOnly','false'),
    # ('returnDistinctValues','false'),
    # ('cacheHint','false'),
    # ('orderByFields','FID%20ASC'),
    # ('groupByFieldsForStatistics',''),
    # ('outStatistics',''),
    # ('having',''),
    # ('resultOffset',0),
    # ('resultRecordCount',50),
    # ('sqlFormat','none'),
    # ('pjson',''),
    # ('token','')
    # )

    params = (
        ('f', 'json'),
        ('where', "(Datum >= timestamp '{}') AND (Datum < timestamp '{}')".format(dateFrom, dateTo)),
        ('outFields', 'Datum,Region,Neue_Faelle'),
        ('resultRecordCount', MAX_RESULT_ROWS),  # max value
        ('resultOffset', 0),
        ('sqlFormat', 'standard')
    )
    try:
        response = requests.get(endpointUrl, params=params)
        response_json = response.json()
        return response_json
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        raise SystemExit(errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        raise SystemExit(errh)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        raise SystemExit(errh)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
        raise SystemExit(errh)
    except:
        print("exception")
        return None


def get_corona_cases(dateFrom, dateTo) -> pd.DataFrame:

    df_cleaned = pd.DataFrame()

    while dateFrom <= dateTo:

        print("Fetching cases from API from '{}' to '{}'".format(
            dateFrom, dateFrom + timedelta(days=MAX_DAYS_PER_REQUEST) if dateFrom + timedelta(days=MAX_DAYS_PER_REQUEST) < dateTo else dateTo))
        response = fetch_corona_data(dateFrom, dateTo)
        df_response_json = pd.json_normalize(response['features'])

        if df_response_json.empty:
            print('Nothing to do')
            return None

        columnnames = [str.replace(col, 'attributes.', '') for col in df_response_json.columns]
        df_response_json.columns = columnnames

        df_response_json['Datum'] = pd.to_datetime(df_response_json['Datum'], unit='ms')
        df_response_json.Region = df_response_json.Region.astype('category')
        df_response_json.Neue_Faelle = df_response_json.Neue_Faelle.astype('int')

        df_cleaned = df_cleaned.append(df_response_json[['Datum', 'Region', 'Neue_Faelle']])
        dateFrom = dateFrom + timedelta(days=MAX_DAYS_PER_REQUEST)

    return df_cleaned
