import pandas as pd


def get_municipalities_df():
    url_municipalities = 'https://www.agvchapp.bfs.admin.ch/de/communes/results?EntriesFrom=01.01.2021&EntriesTo=01.01.2021&UseDefaultDates=True&Canton=GR'

    dfs = pd.read_html(url_municipalities)
    df_municipalities = dfs[0]
    df_municipalities.rename(columns={'BFS-Gde Nummer':'BFS_Nr','Bezirks-nummer':'Bezirks_Nr','Datum der Aufnahme':'Aufnahmedatum', 'Datum der Aufhebung':'Aufhebungsdatum', 'Hist.-Nummer':'Hist_Nr'}, inplace=True)
    df_municipalities = df_municipalities[['BFS_Nr','Gemeindename','Bezirks_Nr','Bezirksname','Kanton', 'Aufnahmedatum', 'Aufhebungsdatum', 'Hist_Nr']]
    df_municipalities.set_index('BFS_Nr',inplace=True)
    return df_municipalities


if __name__ == '__main__':
    print(get_municipalities_df().head())