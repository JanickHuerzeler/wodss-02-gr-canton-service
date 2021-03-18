# %%
import pandas as pd


def get_cantons_metadata_df():
    regionalporträts_2020_kennzahlen_aller_gemeinden ='https://www.bfs.admin.ch/bfsstatic/dam/assets/11587763/master'
    data = pd.read_excel(r'https://www.bfs.admin.ch/bfsstatic/dam/assets/11587763/master')
    df = pd.DataFrame(data)
    df = df.dropna()
    df.columns = data.loc[4].values
    df = df.iloc[1:]
    df_population_for_bfsNr = df[['Gemeindecode', 'Gemeindename','Einwohner']]
    df_population_for_bfsNr.reset_index(inplace=True)
    df_population_for_bfsNr = df_population_for_bfsNr.drop(['index'], axis=1)
    df_population_for_bfsNr.set_index('Gemeindecode',inplace=True)
    return df


if __name__ == '__main__':
    get_cantons_metadata_df()

 

