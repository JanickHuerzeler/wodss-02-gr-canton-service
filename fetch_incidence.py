# Entry point for incidence fetching
# Used for initial incidence fetching
# Used for incremental incidence fetching

# Entry point will be called via CLI with arguments
# https://docs.python.org/3/library/argparse.html

import argparse
import pandas as pd
from datetime import datetime, timedelta
import modules.process_incidence.fetch_corona_data as fcd
import modules.process_incidence.process_corona_data as pcd
import modules.process_municipality.process_municipality_data as pmd
import modules.process_incidence.db as idb
import logging

# Read logger config (CLI is directly callable!)
logging.config.fileConfig(fname='log.conf')
logger = logging.getLogger(__file__)

parser = argparse.ArgumentParser(
    description='Entry point for incidence fetching and calculation')
parser.add_argument('--save_to_db', help='When provided, the incidences get saved to the database',
                    required=False, default=False, action='store_true')
parser.add_argument('--full_dataset', help='When provided, all data is being loaded ',
                    required=False, default=False, action='store_true')
args = parser.parse_args()

save_to_db: bool = args.save_to_db
full_dataset: bool = args.full_dataset

logger.info(
    f'CLI for incidence fetching and calculation was started. (save_to_db: {save_to_db}, full_dataset: {full_dataset})')

try:
    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if full_dataset:    
        earliest_date_with_data = datetime(2020, 2, 26, 0, 0)
        logger.debug(f'Getting corona cases from GR API. (dateFrom: {earliest_date_with_data}, dateTo: {now})')
        df_corona_cases = fcd.get_corona_cases(earliest_date_with_data, now)
    else:
        # Check the last fetch date in DB
        last_fetch_date = idb.get_last_import_date()
        last_fetch_date = datetime(
            last_fetch_date.year, last_fetch_date.month, last_fetch_date.day, 0, 0)
        logger.debug(f'Getting corona cases from GR API. (dateFrom: {last_fetch_date}, dateTo: {now})')
        # Fetch difference to now
        df_corona_cases = fcd.get_corona_cases(
            last_fetch_date + timedelta(days=1), now)
        df_db_corona_cases = idb.get_last_14_imported_days(last_fetch_date)

    # Do not proceed if there are no new datasets...
    df_cumsum_and_incidence_length: int = 0
    sum_new_cases: int = 0
    if df_corona_cases is not None:
        # Save API case count for validation
        sum_cases_recevied_by_api = df_corona_cases['Neue_Faelle'].sum()

        # Get all municipalities
        df_municipality = pmd.get_municipalities()
        # Assign cases without region
        df_all_cases_assigned_to_regions = pcd.distribute_cases_without_region(
            df_municipality, df_corona_cases)
        # Save case count after assignment of cases wihtout region for validation
        sum_cases_after_assigment_of_without_region = df_all_cases_assigned_to_regions[['Bezirksname', 'Datum', 'Neue_Faelle_Region']].drop_duplicates()[
            'Neue_Faelle_Region'].sum()

        # Distribute cases from regions to municipalities
        df_all_cases_distributed_to_municipalities = pcd.distribute_region_cases_to_municipalities(
            df_municipality, df_all_cases_assigned_to_regions)
        # Save case count after distribution to municipalities for validation
        sum_cases_after_municipality_distribution = df_all_cases_assigned_to_regions['Neue_Faelle_Gemeinde'].sum(
        )

        # If incremental import is executed, prepend the last 14 days from DB to the new days
        if full_dataset == False:
            df_all_cases_distributed_to_municipalities = df_db_corona_cases.append(
                df_all_cases_distributed_to_municipalities)
            df_all_cases_distributed_to_municipalities.reset_index(inplace=True)

        # Calcuate cumsum and incidence of 14 days
        df_cumsum_and_incidence = pcd.calculate_cumsum_and_incidence(
            df_all_cases_distributed_to_municipalities)

        # If incremental import is executed, filter all days which are already in DB
        if full_dataset == False:
            df_cumsum_and_incidence['Datum'] = pd.to_datetime(
                df_cumsum_and_incidence['Datum'])
            df_cumsum_and_incidence = df_cumsum_and_incidence[
                df_cumsum_and_incidence['Datum'] > last_fetch_date]

        df_cumsum_and_incidence_length = len(df_cumsum_and_incidence)
        sum_new_cases = df_cumsum_and_incidence['Neue_Faelle_Gemeinde'].sum()

        logger.debug(f'Sum of cases received by GR API: {sum_cases_recevied_by_api}')
        logger.debug(f'Sum of cases after distribution of cases without region: {sum_cases_after_assigment_of_without_region}')
        logger.debug(f'Sum of cases after distribution from region to municipalities: {sum_cases_after_municipality_distribution}')
        logger.debug(f'Sum of cases after incidence and cumsum calculation: {sum_new_cases}')    

        if(save_to_db):
            idb.save_to_db(df_cumsum_and_incidence)

    logger.info(
    f'CLI for incidence fetching and calculation has ended. (save_to_db: {save_to_db}, full_dataset: {full_dataset}, new rows fetched: {len(df_corona_cases) if df_corona_cases is not None else None}, new rows after processing: {df_cumsum_and_incidence_length}, sum new cases: {sum_new_cases})')
except Exception:
    logger.exception('Unhandled exception in CLI for incidence fetching and calculation.')
