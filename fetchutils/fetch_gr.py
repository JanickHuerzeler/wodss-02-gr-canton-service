import requests
import json
import pandas as pd
# Specific implementation, no config files intended for "exchangeability".


def get_canton_data() -> str:
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
        ('where', '1=1'),
        ('outFields', '*'),
    )
    try:
        response = requests.get(endpointUrl, params=params)
        response_json = response.json()

        # print(f'objectIdFieldName: { response_json['objectIdFieldName'] }')
        # print(f'globalIdFieldName: {response_json['globalIdFieldName']}')
        # print(f'fields: {response_json['fields']}')
        # print(f'exceededTransferLimit: {response_json['exceededTransferLimit']}')
        # print(f'features: {response_json['features']}')
        # print(f'uniqueIdField.name: {response_json['uniqueIdField.name']}')
        # print(f'uniqueIdField.isSystemMaintained: {response_json['uniqueIdField.isSystemMaintained']}')

        return response_json
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        raise SystemExit(e)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        raise SystemExit(e)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        raise SystemExit(e)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
        raise SystemExit(e)
    except:
        print("exception")
        return None


def get_canton_data_df():

    response = get_canton_data()
    df_response_json = pd.json_normalize(response['features'])
    columnnames = [str.replace(col, 'attributes.', '') for col in df_response_json.columns]
    df_response_json.columns = columnnames

    df_response_json['Datum'] = pd.to_datetime(df_response_json['Datum'], unit='ms')
    df_response_json.Region = df_response_json.Region.astype('category')
    df_response_json.Neue_Faelle = df_response_json.Neue_Faelle.astype('int')
    df_response_json.Aktive_Faelle = df_response_json.Aktive_Faelle.astype('int')
    df_response_json.Faelle__kumuliert_ = df_response_json.Faelle__kumuliert_.astype('int')
    df_response_json.Verstorbene = df_response_json.Verstorbene.astype('int')
    df_response_json.Verstorbene__kumuliert_ = df_response_json.Verstorbene__kumuliert_.astype('int')
    df_response_json.FID = df_response_json.FID.astype('int')

    df_cleaned = df_response_json[['Datum', 'Region', 'Neue_Faelle']]
    df_cleaned = df_cleaned.groupby(['Region', 'Datum']).sum()

    return df_cleaned


if __name__ == '__main__':
    print(get_canton_data_df().head())
