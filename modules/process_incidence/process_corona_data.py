import collections
import pandas as pd
import numpy as np
import itertools

INCIDENCE_POPULATION_REFERENCE = 100_000


def distribute_cases_without_region(df_municipalities, df_cases):

    set_bezirksnamen = set(sorted(df_municipalities['Bezirksname']))  # From Municipality Stammdaten
    set_regionen = set(sorted(df_cases['Region']))  # From Cases, i.e. the region a case belongs to

    # Region (from Cases): Bezirksname (from Municipalities)
    dict_bezirks_mapping = {'Albula': 'Albula',
                            'Bernina': 'Bernina',
                            'Engiadina Bassa/Val Müstair': 'Engiadina B./Val Müstair',
                            'Imboden': 'Imboden',
                            'Landquart': 'Landquart',
                            'Maloja': 'Maloja',
                            'Moesa': 'Moesa',
                            'Plessur': 'Plessur',
                            'Prättigau/Davos': 'Prättigau / Davos',
                            'Surselva': 'Surselva',
                            'Viamala': 'Viamala'}

    df_cases['Bezirksname'] = df_cases['Region'].apply(lambda region: dict_bezirks_mapping.get(region))

    # Calculate share of population per region in GR
    df_inhabtiants_per_region = df_municipalities.groupby(
        ['Bezirksname'])['Einwohner'].sum().reset_index().set_index('Bezirksname')
    df_inhabtiants_per_region['Anteil_Einwohner_an_GR'] = df_inhabtiants_per_region['Einwohner'] / \
        df_inhabtiants_per_region['Einwohner'].sum()

    # Find all case rows without a region
    df_cases_without_region = df_cases[df_cases['Bezirksname'].isnull()].copy()

    # List of regions
    lst_region = list(df_inhabtiants_per_region.index)
    # List of population shares
    lst_population_share = list(df_inhabtiants_per_region['Anteil_Einwohner_an_GR'])

    # With choice 1, we choose one Bezrik to inherit all the cases on purpose (with weighted randomization)
    df_cases_without_region['Bezirksname'] = df_cases_without_region['Bezirksname'].apply(
        lambda _: np.random.choice(lst_region, 1, p=lst_population_share)[0])

    # Filter out all case rows which are assigned to a region
    df_cases = df_cases[~df_cases['Bezirksname'].isna()]

    # Append the cases which were previously not assigned to a region to the original cases dataframe
    # Results in duplicate entry for one date and one region
    df_extended_cases = df_cases.append(df_cases_without_region)

    # Resolve duplicate entry for one date and region by grouping and summing it
    df_extended_cases = df_extended_cases.groupby(['Datum', 'Bezirksname'])['Neue_Faelle'].sum().reset_index()

    # Store BFS_Nr as columns in municipality dataframe
    df_municipalities['BFS_Nr'] = df_municipalities.index

    # Merge municipality and cases dataframe
    df_municipality_cases = pd.merge(df_municipalities, df_extended_cases, how='inner',
                                     left_on='Bezirksname', right_on='Bezirksname')
    df_municipality_cases.rename(columns={'Neue_Faelle': 'Neue_Faelle_Region'}, inplace=True)

    return df_municipality_cases


def distribute_region_cases_to_municipalities(df_municipalities, df_municipality_cases):
    # Create a crosstable of Bezirke and BFS_Nr (as list)
    df_bezirk_gemeinden = df_municipalities.groupby('Bezirksname')['BFS_Nr'].apply(
        list).reset_index().set_index('Bezirksname').T

    # Create a crosstable of Bezirke and date for cases
    df_cases_bezirk = df_municipality_cases[['Datum', 'Bezirksname', 'Neue_Faelle_Region']].drop_duplicates()
    df_cases_bezirk = df_cases_bezirk.groupby(['Datum', 'Bezirksname']).sum()
    df_cases_bezirk = df_cases_bezirk.unstack()
    df_cases_bezirk = df_cases_bezirk.fillna(0)

    # Create grouped dataframe by Bezirk and BFS_Nr for area per Gemeinde
    lst_anteil_flaeche_bezirk_gemeinden = df_municipalities.groupby(['Bezirksname', df_municipalities.index])[
        'Anteil_Flaeche_in_Region'].apply(list)
    lst_anteil_flaeche_bezirk_gemeinden

    # Initialize result dataframe
    df_cases_distributed_per_gemeinde = df_municipality_cases
    # Add new column for municipality distribution to dataframe
    df_cases_distributed_per_gemeinde['Neue_Faelle_Gemeinde'] = 0

    # Loop through all Bezirke
    for bezirk in df_bezirk_gemeinden:
        print("Distribute cases of Bezirk: {}".format(bezirk))

        # Loop thorugh all gemeinde BFS_Nr
        for bezirk_bfs_nrs in df_bezirk_gemeinden[bezirk].values:
            #print("BFS_Nrs: {}".format(bezirk_bfs_nrs))

            # Getting all available dates
            unique_dates = df_cases_bezirk['Neue_Faelle_Region'].reset_index()['Datum'].unique()
            for date in unique_dates:
                #print("Distribute cases of Bezirk '{}' and date '{}'".format(bezirk, date))

                # Flatten gemeinde / area list
                lst_anteil_flaeche_bezirk_gemeinden_flat = itertools.chain(
                    *lst_anteil_flaeche_bezirk_gemeinden[bezirk].values)
                flaechen_bezirk = list(lst_anteil_flaeche_bezirk_gemeinden_flat)

                # Random distribution of cases in given Region for given date
                choices_per_region = get_choices_for_faelle(
                    bezirk_bfs_nrs, df_cases_bezirk['Neue_Faelle_Region'].loc[date][bezirk].astype(int), flaechen_bezirk)

                # Create new dataframe for given Gemeinden based on random choice and assign cases
                df_faelle_per_gemeinde = pd.DataFrame(df_cases_distributed_per_gemeinde[
                    (df_cases_distributed_per_gemeinde['Datum'] == date) &
                    (df_cases_distributed_per_gemeinde['BFS_Nr'].isin(bezirk_bfs_nrs))
                ]['BFS_Nr'].apply(lambda bfsnr: choices_per_region.get(bfsnr, 0)))
                df_faelle_per_gemeinde.rename(columns={'BFS_Nr': 'Neue_Faelle_Gemeinde'}, inplace=True)

                # Update total dataframe with distributed cases
                df_cases_distributed_per_gemeinde.update(df_faelle_per_gemeinde)

    # Verify result
    # print(df_cases_distributed_per_gemeinde.tail(20))
    # print("Sum Neue_Faelle_Region: {}".format(df_cases_distributed_per_gemeinde[['Bezirksname', 'Datum', 'Neue_Faelle_Region']].drop_duplicates()['Neue_Faelle_Region'].sum()))
    # print("Sum Neue_Faelle_Gemeinde: {}".format(df_cases_distributed_per_gemeinde['Neue_Faelle_Gemeinde'].sum()))

    return df_cases_distributed_per_gemeinde


def get_choices_for_faelle(gemeinden, faelle: int, flaeche):
    # Choose which BFSNrs (as passed in list 'gemeinden'), get how many of the faelle
    random_choices = np.random.choice(gemeinden, faelle, p=flaeche)
    # Count the random choices
    counter = collections.Counter(random_choices)
    # Get the number of choices our "current choice" has got
    return counter


def calculate_cumsum_and_incidence(df_cases_distributed_per_municipality):

    # Add new column for rolling 14 days sum to dataframe
    df_cases_distributed_per_municipality.loc[:, 'Rolling_Sum'] = 0
    # Add new column for  14 days incidence to dataframe
    df_cases_distributed_per_municipality.loc[:, '14d_Incidence'] = 0

    for gemeinde in df_cases_distributed_per_municipality['Gemeindename'].unique():
        print("Calculate cumsum and incidence for Gemeinde: {}".format(gemeinde))
        # Create a pandas series for current municipality containing the rolling 14 days sum
        # ATTENTION: We use 'shift(1)' because the 14 days incidence must be calculated based on the 14 days before today but assigned to todays date
        # Example 01.02.2021 - 14.02.2021 is the incidence persented on 15.02.2021!
        series_rolling_sum = df_cases_distributed_per_municipality[df_cases_distributed_per_municipality['Gemeindename']
                                                                   == gemeinde]['Neue_Faelle_Gemeinde'].shift(1).rolling(14).sum()
        # Create a pandas series of the same size as series_rolling_sum with population number of municipality (always same number)
        series_einwohner = df_cases_distributed_per_municipality[df_cases_distributed_per_municipality['Gemeindename']
                                                                 == gemeinde]['Einwohner']
        # Calcucate incidence based on rolling_sum and einwohner series over the whole series
        series_incidence = calculate_incidence(series_rolling_sum, series_einwohner)

        # Create rolling sum dataframe
        df_rolling_sum = pd.DataFrame(columns=['Rolling_Sum'])
        df_rolling_sum['Rolling_Sum'] = series_rolling_sum

        # Create incidence dataframe
        df_incidence = pd.DataFrame(columns=['14d_Incidence'])
        df_incidence['14d_Incidence'] = series_incidence

        # Update Rolling_Sum and 14d_Incidence columns in result dataframe
        df_cases_distributed_per_municipality.update(df_rolling_sum)
        df_cases_distributed_per_municipality.update(df_incidence)

    return df_cases_distributed_per_municipality


def calculate_incidence(series_rolling_sum: pd.Series, series_population: pd.Series):
    return (series_rolling_sum / series_population) * INCIDENCE_POPULATION_REFERENCE
