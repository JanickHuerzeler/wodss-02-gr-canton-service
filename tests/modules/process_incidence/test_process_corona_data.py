import pytest
import os
import math
import pandas as pd
from pandas.testing import assert_series_equal
from modules.process_incidence.process_corona_data import distribute_cases_without_region, calculate_incidence


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
    assert df_cases_per_region['Neue_Faelle_Region'].sum() == df_cases['Neue_Faelle'].sum() 
    assert df_cases_per_region[df_cases_per_region['Bezirksname']
                               == 'ohne Wohnsitz']['Neue_Faelle_Region'].sum() == 0


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