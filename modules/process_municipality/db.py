import pandas as pd
from sqlalchemy import create_engine
from app import db


def save_to_db(df_municipalities):
    """
    Writes the municipalities of GR into the database with their corresponding info about region, area and population.
    """

    engine = db.get_engine()
    df_municipalities = df_municipalities.reset_index()

    dict_db_cols = {'BFS_Nr': 'bfsNr', 'Gemeindename': 'name', 'Kanton': 'canton',
                    'Gesamtflaeche_in_km2': 'area', 'Einwohner': 'population', 'Bezirksname': 'region'}

    df_db = df_municipalities[dict_db_cols.keys()].copy()
    df_db.rename(columns=dict_db_cols, inplace=True)

    df_db.to_sql('municipality', engine, if_exists='append', index=False)
