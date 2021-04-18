import pytest
import pandas as pd
from modules.process_municipality.process_municipality_data import get_municipalities

def test_get_municipalities(monkeypatch):
    # Given (Mock data)
    def mock_get_municipalities_df():
        df_municipalities = pd.read_csv('tests/modules/process_municipality/testdata/df_municipalities_20210418.csv', sep=';')
        df_municipalities = df_municipalities.set_index('BFS_Nr')
        return df_municipalities

    def mock_get_cantons_metadata_df():
        df_metadata = pd.read_csv('tests/modules/process_municipality/testdata/df_population_for_bfsNr_20210418.csv', sep=';')
        df_metadata = df_metadata.set_index('BFS_Nr')
        return df_metadata
        
    monkeypatch.setattr('modules.process_municipality.fetch_municipalities.get_municipalities_df', mock_get_municipalities_df)
    monkeypatch.setattr('modules.process_municipality.fetch_cantons_metadata.get_cantons_metadata_df', mock_get_cantons_metadata_df)

    # When
    df_municipalities = get_municipalities()

    # Then
    assert 'Anteil_Flaeche_in_Region' in df_municipalities.columns
    assert 'Gesamtflaeche_in_km2' in df_municipalities.columns
    assert 'Bezirksname' in df_municipalities.columns
    assert 'Gemeindename' in df_municipalities.columns
    assert 'Gemeindename_y' not in df_municipalities.columns 
    assert 'Gemeindename_x' not in df_municipalities.columns
    assert 'BFS_Nr' == df_municipalities.index.name
    assert len(df_municipalities) == 101
    


