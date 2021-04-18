import pytest
import os
import math
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
from modules.process_incidence.process_corona_data import distribute_cases_without_region, calculate_incidence, get_choices_for_faelle, distribute_region_cases_to_municipalities, calculate_cumsum_and_incidence

# distribute_cases_without_region


def test_distribute_cases_without_region_same_cases():
    # Given (mock data)
    df_cases = pd.read_csv(
        "tests/modules/process_incidence/testdata/corona_cases_gr_20200301_20200531.csv", sep=";")
    df_municipalities = pd.read_csv(
        "tests/modules/process_incidence/testdata/municipalities_gr.csv", sep=";")
    df_municipalities = df_municipalities.set_index('BFS_Nr')

    cases_ohne_wohnsitz = 58

    # Pre-cecks (Test cases match before)
    assert df_cases[df_cases['Region'] ==
                    'ohne Wohnsitz']['Neue_Faelle'].sum() == cases_ohne_wohnsitz

    # When
    df_municipalities_with_cases_per_region = distribute_cases_without_region(
        df_municipalities, df_cases)

    # Then
    # Check renamed columns
    assert 'Neue_Faelle_Region' in df_municipalities_with_cases_per_region.columns
    assert 'Bezirksname' in df_municipalities_with_cases_per_region.columns

    df_cases_per_region = df_municipalities_with_cases_per_region[[
        'Datum', 'Bezirksname', 'Neue_Faelle_Region']].drop_duplicates()

    # Check total is the same, but ohne Wohnsitz are 0
    assert df_cases_per_region['Neue_Faelle_Region'].sum(
    ) == df_cases['Neue_Faelle'].sum()
    assert df_cases_per_region[df_cases_per_region['Bezirksname']
                               == 'ohne Wohnsitz']['Neue_Faelle_Region'].sum() == 0

# calculate_incidence


def test_calculate_incidence():
    # Given
    series_14d_cases_sum = pd.Series([15, 130])
    series_population = pd.Series([15000, 250000])

    # When
    series_incidence_result = calculate_incidence(
        series_14d_cases_sum, series_population)

    # Then
    series_incidence_expected = pd.Series([100.0, 52.0])
    assert_series_equal(series_incidence_expected, series_incidence_result)


def test_calculate_incidence_zero_cases():
    # Given
    series_14d_cases_sum = pd.Series([0])
    series_population = pd.Series([17000])

    # When
    series_incidence_result = calculate_incidence(
        series_14d_cases_sum, series_population)

    # Then
    series_incidence_expected = pd.Series([0.0])
    assert_series_equal(series_incidence_expected, series_incidence_result)


def test_calculate_incidence_zero_population():
    # Given
    series_14d_cases_sum = pd.Series([100])
    series_population = pd.Series([0])

    # When
    series_incidence_result = calculate_incidence(
        series_14d_cases_sum, series_population)

    # Then
    series_incidence_expected = pd.Series([math.inf])
    assert_series_equal(series_incidence_expected, series_incidence_result)


# get_choices_for_faelle
def test_get_choices_for_faelle():
    # Given
    lst_gemeinden = list([1234, 1235, 1236])
    anz_faelle = 4
    lst_gemeinde_flaechen = list([0.658, 0.142, 0.2])

    # When
    result = get_choices_for_faelle(
        lst_gemeinden, anz_faelle, lst_gemeinde_flaechen)

    # Then
    assert sum(result.values()) == anz_faelle


def test_get_choices_for_faelle_zero_cases():
    # Given
    lst_gemeinden = list([1234, 1235, 1236])
    anz_faelle = 0
    lst_gemeinde_flaechen = list([0.658, 0.142, 0.2])

    # When
    result = get_choices_for_faelle(
        lst_gemeinden, anz_faelle, lst_gemeinde_flaechen)

    # Then
    assert sum(result.values()) == anz_faelle


# distribute_region_cases_to_municipalities
def test_distribute_region_cases_to_municipalities():
    # Given
    df_municipalities = pd.read_csv(
        "tests/modules/process_incidence/testdata/municipalities_gr.csv", sep=";")

    df_cases_region_distributed = pd.read_csv(
        'tests/modules/process_incidence/testdata/corona_cases_gr_distributed_ohne_Wohnsitz.csv', sep=';')
    total_cases_by_bezirk = df_cases_region_distributed[[
        'Datum', 'Bezirksname', 'Neue_Faelle_Region']].drop_duplicates()
    # Convert int to float for exact compare
    total_cases_by_bezirk['Neue_Faelle_Region'] = total_cases_by_bezirk['Neue_Faelle_Region'].astype(
        float)

    total_cases = sum(total_cases_by_bezirk['Neue_Faelle_Region'])

    # When
    result_cases_distributed_by_gemeinde = distribute_region_cases_to_municipalities(
        df_municipalities, df_cases_region_distributed)

    result_total_cases = sum(
        result_cases_distributed_by_gemeinde['Neue_Faelle_Gemeinde'])
    result_by_bezirk = result_cases_distributed_by_gemeinde.groupby(
        ['Datum', 'Bezirksname'])['Neue_Faelle_Gemeinde'].sum().reset_index()
    result_by_bezirk.rename(
        columns={'Neue_Faelle_Gemeinde': 'Neue_Faelle_Region'}, inplace=True)

    # Then
    assert 'Neue_Faelle_Gemeinde' in result_cases_distributed_by_gemeinde.columns
    assert total_cases == result_total_cases
    # Compare data frames with cases per region and date
    assert_frame_equal(total_cases_by_bezirk.sort_values(by=['Datum', 'Bezirksname', 'Neue_Faelle_Region']).reset_index(
        drop=True), result_by_bezirk.sort_values(by=['Datum', 'Bezirksname', 'Neue_Faelle_Region']).reset_index(drop=True))


# calculate_cumsum_and_incidence


def test_calculate_cumsum_and_incidence_edge_days_with_non_zero():
    # Given
    result_cases_distributed_by_gemeinde = pd.read_csv(
        'tests/modules/process_incidence/testdata/corona_cases_gr_distributed_per_municipality.csv', sep=';')

    bfs_nr = 3871  # Population of 3871 is: 4451
    date_from = '2020-03-20'
    date_to = '2020-04-20'
    test_data = result_cases_distributed_by_gemeinde[(result_cases_distributed_by_gemeinde['BFS_Nr'] == bfs_nr) &
                                                     (result_cases_distributed_by_gemeinde['Datum'] >= date_from) &
                                                     (result_cases_distributed_by_gemeinde['Datum'] <= date_to)].copy()

    calc_date = '2020-04-08'
    rolling_sum = 7.0
    incidence = 157.26802965625702  # rolling_sum / population * 1_000_000

    # When
    result = calculate_cumsum_and_incidence(test_data)

    result_row = result.loc[(result['BFS_Nr'] == bfs_nr) &
                            (result['Datum'] == calc_date)
                            ].copy()

    # Then
    assert 'Rolling_Sum' in result.columns
    assert '14d_Incidence' in result.columns
    assert len(result_row) == 1
    assert result_row.iloc[0]['Rolling_Sum'] == rolling_sum
    assert result_row.iloc[0]['14d_Incidence'] == incidence


def test_calculate_cumsum_and_incidence_first_day_of_sequence():
    # Given
    result_cases_distributed_by_gemeinde = pd.read_csv(
        'tests/modules/process_incidence/testdata/corona_cases_gr_distributed_per_municipality.csv', sep=';')

    bfs_nr = 3871  # Population of 3871 is: 4451
    date_from = '2020-03-20'
    date_to = '2020-04-20'
    test_data = result_cases_distributed_by_gemeinde.loc[(result_cases_distributed_by_gemeinde['BFS_Nr'] == bfs_nr) &
                                                         (result_cases_distributed_by_gemeinde['Datum'] >= date_from) &
                                                         (result_cases_distributed_by_gemeinde['Datum'] <= date_to)].copy()

    calc_date = '2020-03-20'
    rolling_sum = 0
    incidence = 0  # rolling_sum / population * 1_000_000

    # When
    result = calculate_cumsum_and_incidence(test_data)

    result_row = result.loc[(result['BFS_Nr'] == bfs_nr) &
                            (result['Datum'] == calc_date)
                            ].copy()

    # Then
    assert 'Rolling_Sum' in result.columns
    assert '14d_Incidence' in result.columns
    assert len(result_row) == 1
    assert result_row.iloc[0]['Rolling_Sum'] == rolling_sum
    assert result_row.iloc[0]['14d_Incidence'] == incidence
