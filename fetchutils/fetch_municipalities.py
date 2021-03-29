import pandas as pd
import os.path
import requests
from configManager import ConfigManager

# TODO: if colorful printing would be useful, use a library for this
# colorful print messages, found at: https://stackoverflow.com/a/287944 
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_municipalities_df_with_file_check(useExcelDownload: bool = False, forceUrlDownload: bool = True, verbose = False) -> pd.DataFrame:
    """Returns pandas DataFrame
    
    All municipalities of GR with info about bfsNr, municipality name, area name and canton name.

    Arguments:

        useExcelDownload (default = False): use html scrapper if False, use excel download if True.

        forceUrlDownload (default = False): force a fresh download of the municipalities data from the source web page.

        verbose (default = False):          print additional debug statements if True.

    """

    # get configuration for download urls and filenames
    cfgm = ConfigManager.get_instance().get_bfs_community_booth_configuration()

    # declare df_municipalities for later assignment
    df_municipalities = None

    # output
    excel_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'data', cfgm['excelFileName']))

    # if excel file does not exist, download and save it previously
    if os.path.isfile(excel_file_path) and forceUrlDownload is False:
        if verbose: print(f"{bcolors.OKGREEN}{excel_file_path} exists and no datasource reload forced. Reading {excel_file_path} now...{bcolors.ENDC}")
        
        dfs = pd.read_excel(excel_file_path)
        df_municipalities = dfs
        if verbose: print(f"{bcolors.OKGREEN}Done reading {excel_file_path}.{bcolors.ENDC}")
    else:
        if forceUrlDownload is False:
            if verbose: print(f"{bcolors.WARNING}{excel_file_path} does not exist.{bcolors.ENDC}") 
        if verbose: print(f"{bcolors.OKCYAN}Fetching data from {cfgm['dataSourcePostUrl'] if useExcelDownload is True else cfgm['dataSourceHtmlUrl']}.{bcolors.ENDC}")
        
        if useExcelDownload is True:
            # use excel download
            response = requests.post(cfgm['dataSourcePostUrl'])
            excelData = response.content
            dfs = pd.read_excel(excelData)
            df_municipalities = dfs
        else: 
            # use html scrapper
            url_municipalities = cfgm['dataSourceHtmlUrl']
            dfs = pd.read_html(url_municipalities)
            df_municipalities = dfs[0]
        
        # write file down to disk
        with pd.ExcelWriter(excel_file_path) as writer: 
            df_municipalities.to_excel(writer)
    
    if useExcelDownload is False:
        df_municipalities.rename(columns={'BFS-Gde Nummer': 'BFS_Nr', 'Bezirks-nummer': 'Bezirks_Nr', 
            'Datum der Aufnahme': 'Aufnahmedatum', 'Datum der Aufhebung': 'Aufhebungsdatum', 'Hist.-Nummer': 'Hist_Nr'}, inplace=True)
    else:
        df_municipalities.rename(columns={'BFS Gde-nummer': 'BFS_Nr', 'Bezirks-nummer': 'Bezirks_Nr', 
            'Datum der Aufnahme': 'Aufnahmedatum', 'Hist.-Nummer': 'Hist_Nr'}, inplace=True)

    df_municipalities = df_municipalities[df_municipalities['Kanton'] == 'GR']
    
    df_municipalities = df_municipalities[['BFS_Nr', 'Gemeindename', 'Bezirksname', 'Kanton']]
    df_municipalities.set_index('BFS_Nr', inplace=True)

    
    if verbose: print(f"{bcolors.OKBLUE}{df_municipalities}{bcolors.ENDC}") 
    return df_municipalities


def get_municipalities_df():
    # get configuration for download urls and filenames
    cfgm = ConfigManager.get_instance().get_bfs_community_booth_configuration()
    url_municipalities = cfgm['dataSourceHtmlUrl']

    dfs = pd.read_html(url_municipalities)
    df_municipalities = dfs[0]
    df_municipalities.rename(columns={'BFS-Gde Nummer': 'BFS_Nr', 'Bezirks-nummer': 'Bezirks_Nr',
                             'Datum der Aufnahme': 'Aufnahmedatum', 'Datum der Aufhebung': 'Aufhebungsdatum', 'Hist.-Nummer': 'Hist_Nr'}, inplace=True)
    df_municipalities = df_municipalities[df_municipalities['Kanton'] == 'GR']
    df_municipalities = df_municipalities[['BFS_Nr', 'Gemeindename', 'Bezirksname', 'Kanton']]
    df_municipalities.set_index('BFS_Nr', inplace=True)
    return df_municipalities


if __name__ == '__main__':
    print(get_municipalities_df().head())
