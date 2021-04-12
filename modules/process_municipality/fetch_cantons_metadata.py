import pandas as pd
import os.path
import requests

from configManager import ConfigManager


def get_cantons_metadata_df_with_file_check(forceUrlDownload: bool = False) -> pd.DataFrame:
    """Internal method which decides whether to use a local copy of the excel or fetching a new one.
    Returns pandas DataFrame

    All municipalities of Switzerland with info about bfsNr, municipality name, area in km2 and population.

    Arguments:

        forceUrlDownload (default = False): force a fresh download of the cantons meta data from the source web page.

    """
    print(
        f'get_cantons_metadata_df_with_file_check: forceUrlDownload is set to {forceUrlDownload}.')

    # get configuration for download urls and filenames
    cfgm = ConfigManager.get_instance()
    cf_cm = cfgm.get_canton_metadata_configuration()

    # declare df_municipalities for later assignment
    df_canton_metadata = None

    excel_file_path = os.path.join(cfgm.ROOT_DIR,
                                   'resources', 'municipality_data', cf_cm['excelFileName'])

    # if excel file does not exist, download and save it previously
    if os.path.isfile(excel_file_path) and forceUrlDownload is False:
        print(f"{excel_file_path} exists and no datasource reload forced.")
        print(f"Reading {excel_file_path} now...")

        dfs = pd.read_excel(excel_file_path)
        df_canton_metadata = dfs
        print(f"Done reading {excel_file_path}.")
    else:
        if forceUrlDownload is False:
            print(
                f"{excel_file_path} does not exist. Excel needs to be downloaded...")
        print(f"Fetching data from {cf_cm['dataSourceGetUrl']}.")

        response = requests.get(cf_cm['dataSourceGetUrl'])
        excelData = response.content
        dfs = pd.read_excel(excelData)
        df_canton_metadata = dfs

        # write file down to disk
        with pd.ExcelWriter(excel_file_path) as writer:
            df_canton_metadata.to_excel(writer)
            print(
                f'Excel has been downloaded and persisted to {excel_file_path}.')

    df_canton_metadata = df_canton_metadata.dropna()
    df_canton_metadata.columns = df_canton_metadata.loc[4].values
    df_canton_metadata = df_canton_metadata.iloc[1:]
    df_population_for_bfsNr = df_canton_metadata[[
        'Gemeindecode', 'Gemeindename', 'Einwohner', 'Gesamtfläche in km²']]
    df_population_for_bfsNr.reset_index(inplace=True)
    df_population_for_bfsNr = df_population_for_bfsNr.drop(['index'], axis=1)
    df_population_for_bfsNr.rename(columns={'Gemeindecode': 'BFS_Nr',
                                   'Gesamtfläche in km²': 'Gesamtflaeche_in_km2'}, inplace=True)
    df_population_for_bfsNr.set_index('BFS_Nr', inplace=True)

    # There is no new dataset of municipality metadata provided which contains merged municipalities per 01.01.2021
    # Merge municipality 'Muntogna da Schons' (BFS 3715) from municipalities:
    # Casti-Wergenstein (3703)
    # Donat (3705)
    # Lohn (GR) (3707)
    # Mathon (3708)
    # and add a new series to the df
    series_muntogna_da_schons = df_population_for_bfsNr.loc[[3703, 3705, 3707, 3708]].sum()
    series_muntogna_da_schons['Gemeindename'] = 'Muntogna da Schons'
    series_muntogna_da_schons.name = 3715
    df_population_for_bfsNr = df_population_for_bfsNr.append(series_muntogna_da_schons)

    return df_population_for_bfsNr


def get_cantons_metadata_df(forceUrlDownload: bool = False):
    """Returns pandas DataFrame

    All municipalities of Switzerland with info about bfsNr, municipality name, area in km2 and population.

    Arguments:

        forceUrlDownload (default = False): force a fresh download of the cantons meta data from the source web page.

    """
    return get_cantons_metadata_df_with_file_check(forceUrlDownload=forceUrlDownload)


if __name__ == '__main__':
    print(get_cantons_metadata_df().head())
