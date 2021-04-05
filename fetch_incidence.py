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
import modules.process_municipality.db_import as mun
import modules.process_incidence.db_import as pcdi


parser = argparse.ArgumentParser(
    description='Entry point for municipality fetching')
parser.add_argument('--save_to_db', help='When provided, the municipalities get saved to the database',
                    required=False, default=False, action='store_true')
parser.add_argument('--full_dataset', help='When provided, all data is being loaded ',
                    required=False, default=False, action='store_true')
args = parser.parse_args()

save_to_db: bool = args.save_to_db
full_dataset: bool = args.full_dataset

print('save_to_db:', save_to_db)
print('full_dataset:', full_dataset)

now = datetime.now()
now = now.replace(hour=0, minute=0, second=0, microsecond=0)

if full_dataset:
    df_corona_cases = fcd.get_canton_data_df(datetime(2020, 2, 26, 0, 0), now)
else:
    # Check the last fetch date in DB
    last_fetch_date = pcdi.get_last_import_date()
    last_fetch_date = datetime(last_fetch_date.year, last_fetch_date.month, last_fetch_date.day, 0, 0)
    # Fetch difference to now
    df_corona_cases = fcd.get_canton_data_df(last_fetch_date + timedelta(days=1), now)
    df_db_corona_cases = pcdi.get_last_14_imported_days(last_fetch_date)

# Do not proceed if there are no new datasets...
if df_corona_cases is not None:
    # Save API case count for validation
    sum_cases_recevied_by_api = df_corona_cases['Neue_Faelle'].sum()

    # Get all municipalities
    df_municipality = mun.get_municipalities()
    # Assign cases without region
    df_all_cases_assigned_to_regions = pcd.distribute_cases_without_region(df_municipality, df_corona_cases)
    # Save case count after assignment of cases wihtout region for validation
    sum_cases_after_assigment_of_without_region = df_all_cases_assigned_to_regions[['Bezirksname', 'Datum', 'Neue_Faelle_Region']].drop_duplicates()[
        'Neue_Faelle_Region'].sum()

    # Distribute cases from regions to municipalities
    df_all_cases_distributed_to_municipalities = pcd.distribute_region_cases_to_municipalities(
        df_municipality, df_all_cases_assigned_to_regions)
    # Save case count after distribution to municipalities for validation
    sum_cases_after_municipality_distribution = df_all_cases_assigned_to_regions['Neue_Faelle_Gemeinde'].sum()

    # If incremental import is executed, prepend the last 14 days from DB to the new days
    if full_dataset == False:
        df_all_cases_distributed_to_municipalities = df_db_corona_cases.append(
            df_all_cases_distributed_to_municipalities)
        df_all_cases_distributed_to_municipalities.reset_index()

    # Calcuate cumsum and incidence of 14 days
    df_cumsum_and_incidence = pcd.calculate_cumsum_and_incidence(df_all_cases_distributed_to_municipalities)

    # If incremental import is executed, filter all days which are already in DB
    if full_dataset == False:
        df_cumsum_and_incidence['Datum'] = pd.to_datetime(df_cumsum_and_incidence['Datum'])
        df_cumsum_and_incidence = df_cumsum_and_incidence[df_cumsum_and_incidence['Datum'] > last_fetch_date]

    print(df_cumsum_and_incidence)

    print("Sum of cases received by GR API: {}".format(sum_cases_recevied_by_api))
    print("Sum of cases after distribution of cases without region: {}".format(sum_cases_after_assigment_of_without_region))
    print("Sum of cases after distribution from region to municipalities: {}".format(
        sum_cases_after_municipality_distribution))

    if(save_to_db):
        pcdi.save_to_db(df_cumsum_and_incidence)
