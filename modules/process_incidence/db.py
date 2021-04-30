import pandas as pd
from sqlalchemy import create_engine
from app import db
from datetime import datetime, timedelta


def delete_where_cases_is_null(new_dates):
    if(len(new_dates) >= 1):
        string_dates = [f"'{new_date.strftime('%Y-%m-%d')}'" for new_date in new_dates]
        sep = ', '
        date_filter = sep.join(string_dates)

        sql = f'DELETE FROM public.incidence WHERE cases IS NULL AND date IN ({date_filter});'

        with db.get_engine().connect() as connection:
            result = connection.execute(sql)
            return result


def save_to_db(df_incidences):
    """
    Writes the incidences of GR into the database
    """

    engine = db.get_engine()

    df = df_incidences

    dict_db_cols = {'BFS_Nr': 'bfsNr', 'Datum': 'date', '14d_Incidence': 'incidence',
                    'Neue_Faelle_Gemeinde': 'cases', 'Rolling_Sum': 'cases_cumsum_14d'}

    df_db = df[dict_db_cols.keys()].copy()
    df_db.rename(columns=dict_db_cols, inplace=True)

    df_db.to_sql('incidence', engine, if_exists='append', index=False)


def get_last_import_date():
    max_date = None
    sql = "SELECT max(date) AS max_date FROM public.incidence WHERE cases IS NOT NULL"

    with db.get_engine().connect() as connection:
        result = connection.execute(sql)
        for row in result:
            max_date = row['max_date']

    return max_date


def get_last_14_imported_days(last_import_date) -> pd.DataFrame:
    sql = """   SELECT incidence."bfsNr",
                    incidence.date,
                    incidence.cases, 
                    municipality.population,
                    municipality.area,
                    municipality.name,
                    municipality.region,
                    municipality.canton
                FROM public.incidence
                LEFT JOIN public.municipality ON (incidence."bfsNr" = municipality."bfsNr")
                WHERE date BETWEEN '{}' AND '{}' AND incidence.cases IS NOT NULL
                ORDER BY incidence.date ASC""".format(last_import_date - timedelta(days=14), last_import_date)

    df_db = pd.read_sql_query(sql, db.get_engine())

    dict_db_cols = {
        'population': 'Einwohner',
        'area': 'Gesamtflaeche_in_km2',
        'name': 'Gemeindename',
        'region': 'Bezirksname',
        'canton': 'Kanton',
        'bfsNr': 'BFS_Nr',
        'date': 'Datum',
        'cases': 'Neue_Faelle_Gemeinde'
    }
    df = df_db[dict_db_cols.keys()].copy()
    df.rename(columns=dict_db_cols, inplace=True)

    return df
