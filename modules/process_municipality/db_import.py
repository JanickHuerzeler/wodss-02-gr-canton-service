import pandas as pd
from sqlalchemy import create_engine
import modules.process_municipality.fetch_municipalities as fmp
import modules.process_municipality.fetch_cantons_metadata as fcm
from setup import db


def get_municipalities() -> pd.DataFrame:
    """Returns pandas DataFrame

    All municipalities of GR with info about region, area and population.
    """

    # Fetch all municipalities of GR, by region (Bezirk)
    df_municipalities = fmp.get_municipalities_df()

    # Fetch metadata of all municipalities in GR, i.e. population and area
    df_population_for_bfsNr = fcm.get_cantons_metadata_df()

    # Combine municipality datasets
    # Join by BFS_Nr
    df_all = pd.merge(df_population_for_bfsNr, df_municipalities,
                      how='inner', left_on='BFS_Nr', right_on='BFS_Nr')

    # Handle duplicate column "Gemeindename"
    df_all.rename(columns={'Gemeindename_y': 'Gemeindename'}, inplace=True)
    df_all.drop('Gemeindename_x', axis=1, inplace=True)

    # Summarize area of region
    dict_bezirk_flaechen = dict(df_all.groupby(['Bezirksname'])[
                                'Gesamtflaeche_in_km2'].sum())

    # Calculate share of the municipality area in their region
    df_all['Anteil_Flaeche_in_Region'] = df_all.apply(
        lambda row: row['Gesamtflaeche_in_km2']/dict_bezirk_flaechen[row['Bezirksname']], axis=1)

    return df_all


def save_to_db():
    """
    Writes the municipalities of GR into the database with their corresponding info about region, area and population.
    """

    engine = db.get_engine()
    df = get_municipalities().reset_index()

    dict_db_cols = {'BFS_Nr': 'bfsNr', 'Gemeindename': 'name', 'Kanton': 'canton',
                    'Gesamtflaeche_in_km2': 'area', 'Einwohner': 'population', 'Bezirksname': 'region'}

    df_db = df[dict_db_cols.keys()].copy()
    df_db.rename(columns=dict_db_cols, inplace=True)

    df_db.to_sql('municipality', engine, if_exists='append', index=False)
