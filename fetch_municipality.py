# Entry point for municipality fetching
# Used for initial municipality fetching

# Entry point will be called via CLI with arguments
# https://docs.python.org/3/library/argparse.html

import argparse
import modules.process_municipality.db as mdb
import modules.process_municipality.process_municipality_data as pmd


parser = argparse.ArgumentParser(
    description='Entry point for municipality fetching')
parser.add_argument('--save_to_db', help='When provided, the municipalities get saved to the database',
                    required=False, default=False, action='store_true')

args = parser.parse_args()

save_to_db: bool = args.save_to_db

print('save_to_db:', save_to_db)

df_municipalities = pmd.get_municipalities()

if(save_to_db):
    mdb.save_to_db(df_municipalities)
