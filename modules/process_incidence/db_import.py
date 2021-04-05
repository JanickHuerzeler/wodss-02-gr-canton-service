import pandas as pd
from sqlalchemy import create_engine
from setup import db


def save_to_db(df_incidences):
    """
    Writes the municipalities of GR into the database with their corresponding info about region, area and population.
    """

    engine = db.get_engine()

    df = df_incidences

    dict_db_cols = {'BFS_Nr': 'bfsNr', 'Datum': 'date', '14d_Incidence': 'incidence',
                    'Neue_Faelle_Gemeinde': 'cases', 'Rolling_Sum': 'cases_cumsum_14d'}

    df_db = df[dict_db_cols.keys()].copy()
    df_db.rename(columns=dict_db_cols, inplace=True)

    df_db.to_sql('incidence', engine, if_exists='append', index=False)
