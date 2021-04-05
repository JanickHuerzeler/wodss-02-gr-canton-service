import requests
import json
import pandas as pd
from datetime import date

# Specific implementation, no config files intended for "exchangeability".


# the api is limited to 2000 result items per call
MAX_RESULT_COUNT_PER_REQUEST = 2000
FIRST_DATE_MEASURED_BY_API = date(2020, 2, 26)
AMOUNT_OF_DISTRICTS = 12

def get_canton_data(take: int = 2000, offset=0) -> str:
    ''' 
    Performs a query on the canton endpoint for receiving covid-19 data. See https://curl.trillworks.com/ for request usage.
    '''
    endpointUrl = 'https://services1.arcgis.com/YAuo6vcW85VPu7OE/ArcGIS/rest/services/Fallzahlen_Pro_Region/FeatureServer/0/query'
    print(f'get_canton_data params: take: {take}, offset: {offset}')
    
    params = (
        ('f', 'json'),
        ('where', '1=1'),
        ('outFields', '*'),
        ('resultOffset', f'{offset}'),
        ('resultRecordCount', f'{take}')
    )
    try:
        response = requests.get(endpointUrl, params=params)
        print(response.url)
        response_json = response.json()
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

def get_canton_data_internal(take: int, offset: int):
    response = get_canton_data(take, offset)
    df_response_json = pd.json_normalize(response['features'])
    if not df_response_json.empty:
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
        df_cleaned = df_response_json[['Datum', 'Region', 'Neue_Faelle', 'FID']]
        # df_cleaned = df_cleaned.groupby(['Region', 'Datum']).sum() # Grouping will happen at later point
        return df_cleaned, len(df_cleaned) # return dataframe and amount of items
    else: 
        cols = ['Datum', 'Region', 'Neue_Faelle']
        response = pd.DataFrame(columns=cols)
        return response, 0

def get_canton_data_df_all():

    take = MAX_RESULT_COUNT_PER_REQUEST
    offset = 0
    currentRound = 0
    cols = ['Datum', 'Region', 'Neue_Faelle']
    df_response_all = pd.DataFrame(columns=cols)
    leaveLoop = False
   
    currentDate = date.today()
    dateDelta = currentDate - FIRST_DATE_MEASURED_BY_API
    
    loopInvariant = ((int)((AMOUNT_OF_DISTRICTS * dateDelta.days) /MAX_RESULT_COUNT_PER_REQUEST))+2

    try:
        while leaveLoop is False and currentRound < loopInvariant:
            offset = currentRound * take
            # print(f'Loop: {currentRound}, take: {take}, offset: {offset}')
            iterationData, resultCount = get_canton_data_internal(take, offset)
            # print(f'iterationData: \n {iterationData.head(1)}\n resultCount: {resultCount}')
            df_response_all = df_response_all.append(iterationData[cols],ignore_index=True)
            leaveLoop = True if resultCount < take else False
            currentRound = currentRound + 1
    except Exception as e:
        print(e)

    return df_response_all

def get_canton_data_df():
    return get_canton_data_df_all()
    # response = get_canton_data()
    # df_response_json = pd.json_normalize(response['features'])
    # columnnames = [str.replace(col, 'attributes.', '') for col in df_response_json.columns]
    # df_response_json.columns = columnnames

    # df_response_json['Datum'] = pd.to_datetime(df_response_json['Datum'], unit='ms')
    # df_response_json.Region = df_response_json.Region.astype('category')
    # df_response_json.Neue_Faelle = df_response_json.Neue_Faelle.astype('int')
    # df_response_json.Aktive_Faelle = df_response_json.Aktive_Faelle.astype('int')
    # df_response_json.Faelle__kumuliert_ = df_response_json.Faelle__kumuliert_.astype('int')
    # df_response_json.Verstorbene = df_response_json.Verstorbene.astype('int')
    # df_response_json.Verstorbene__kumuliert_ = df_response_json.Verstorbene__kumuliert_.astype('int')
    # df_response_json.FID = df_response_json.FID.astype('int')

    # df_cleaned = df_response_json[['Datum', 'Region', 'Neue_Faelle']]
    # # df_cleaned = df_cleaned.groupby(['Region', 'Datum']).sum() # Grouping will happen at later point

    # return df_cleaned


if __name__ == '__main__':
    # print(get_canton_data_df().head())
    print(get_canton_data_df_all().head())
