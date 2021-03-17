import requests
import json
# Specific implementation, no config files intended for "exchangeability".

'''
    Performs a query on the canton endpoint for receiving covid-19 data.
    See https://curl.trillworks.com/ for request usage.
'''
def get_canton_data() -> str:
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


if __name__ == '__main__':
    print(get_canton_data())
