import pandas as pd
from sqlalchemy import create_engine
from setup import db
from datetime import datetime, timedelta


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


def get_max_import_date():
    max_date = None
    sql = "SELECT max(date) AS max_date FROM public.incidence"

    with db.get_engine().connect() as connection:
        result = connection.execute(sql)
        for row in result:
            max_date = row['max_date']

    return max_date


def get_last_14_imported_days(last_import_date) -> pd.DataFrame:
    sql = "SELECT * FROM public.incidence WHERE date BETWEEN '{}' AND '{}'".format(
        last_import_date - timedelta(days=14), last_import_date)

    df_db = pd.read_sql_query(sql, db.get_engine())
    print(sql)

    dict_db_cols = {'bfsNr': 'BFS_Nr', 'date': 'Datum', 'incidence': '14d_Incidence',
                    'cases': 'Neue_Faelle_Gemeinde', 'cases_cumsum_14d': 'Rolling_Sum'}
    df = df_db[dict_db_cols.keys()].copy()
    df.rename(columns=dict_db_cols, inplace=True)

    return df
