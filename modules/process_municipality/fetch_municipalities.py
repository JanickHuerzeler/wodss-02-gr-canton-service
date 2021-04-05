import pandas as pd
import os.path
import requests
from configManager import ConfigManager

def get_municipalities_df_with_file_check(forceUrlDownload: bool = False) -> pd.DataFrame:
    """Returns pandas DataFrame
    
    All municipalities of GR with info about bfsNr, municipality name, area name and canton name.

    Arguments:

        forceUrlDownload (default = False): force a fresh download of the municipalities data from the source web page.

    """
    print(f'get_municipalities_df_with_file_check: forceUrlDownload is set to {forceUrlDownload}.')

    # get configuration for download urls and filenames
    cfgm = ConfigManager.get_instance().get_bfs_community_booth_configuration()

    # declare df_municipalities for later assignment
    df_municipalities = None

    excel_file_path = os.path.abspath(os.path.join('resources','municipality_data', cfgm['excelFileName']))

    # if excel file does not exist, download and save it previously
    if os.path.isfile(excel_file_path) and forceUrlDownload is False:
        print(f"{excel_file_path} exists and no datasource reload forced.")
        print(f"Reading {excel_file_path} now...")
        
        dfs = pd.read_excel(excel_file_path)
        df_municipalities = dfs
        print(f"Done reading {excel_file_path}.")
    else:
        if forceUrlDownload is False:
            print(f"{excel_file_path} does not exist. Excel needs to be downloaded...") 
        print(f"Fetching data from {cfgm['dataSourcePostUrl']}.")
    
        response = requests.post(cfgm['dataSourcePostUrl'])
        excelData = response.content
        dfs = pd.read_excel(excelData)
        df_municipalities = dfs
        
        # write file down to disk
        with pd.ExcelWriter(excel_file_path) as writer: 
            df_municipalities.to_excel(writer)
            print(f'Excel has been downloaded and persisted to {excel_file_path}.')
    
    print(f'Preprocessing the output DF now: Renaming columns and removing other cantons than GR...')
    df_municipalities.rename(columns={'BFS Gde-nummer': 'BFS_Nr', 'Bezirks-nummer': 'Bezirks_Nr', 
        'Datum der Aufnahme': 'Aufnahmedatum', 'Hist.-Nummer': 'Hist_Nr'}, inplace=True)

    df_municipalities = df_municipalities[df_municipalities['Kanton'] == 'GR']
    
    df_municipalities = df_municipalities[['BFS_Nr', 'Gemeindename', 'Bezirksname', 'Kanton']]
    df_municipalities.set_index('BFS_Nr', inplace=True)

    print(f'Finished preprocessing. Resulting dataframe:')
    print(f"{df_municipalities}") 
    return df_municipalities


def get_municipalities_df(forceUrlDownload: bool = False):
    """Returns pandas DataFrame
    
    All municipalities of GR with info about bfsNr, municipality name, area name and canton name.

    Arguments:

        forceUrlDownload (default = False): force a fresh download of the municipalities data from the source web page.

    """
    return get_municipalities_df_with_file_check(forceUrlDownload)

if __name__ == '__main__':
    print(get_municipalities_df().head())
