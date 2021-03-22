# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd

# %% [markdown]
# ## Fetch corona cases of GR

# %%
import fetch_gr as fgr


# %%
df_cases = fgr.get_canton_data_df()
df_cases

# %% [markdown]
# ## Fetch all municipalities of GR
# ### by Bezirk

# %%
import fetch_municipalities as fmp


# %%
df_municipalities = fmp.get_municipalities_df()
df_municipalities

# %% [markdown]
# ## Fetch metadata of all municipalities in GR 
# ### i.e. Einwohner and Fläche

# %%
import fetch_cantons_metadata as fcm


# %%
df_population_for_bfsNr = fcm.get_cantons_metadata_df()
df_population_for_bfsNr

# %% [markdown]
# ## Combine the two municipality datasets
# ### i.e. join metadata and Bezirk information

# %%
df_all = pd.merge(df_population_for_bfsNr, df_municipalities , how='inner', left_on='BFS_Nr', right_on='BFS_Nr')
# df_all = df.loc[:,~df.columns.duplicated()]
df_all.rename(columns={'Gemeindename_y': 'Gemeindename'}, inplace=True)
df_all.drop('Gemeindename_x', axis=1, inplace=True)
dict_bezirk_flaechen = dict(df_all.groupby(['Bezirksname'])['Gesamtflaeche_in_km2'].sum())

df_all['Anteil_Flaeche_in_Region'] = df_all.apply(lambda row: row['Gesamtflaeche_in_km2']/dict_bezirk_flaechen[row['Bezirksname']], axis=1)
#display(df_all.groupby(['Bezirksname'])['Anteil_Flaeche_in_Region'].sum())
df_all

# %% [markdown]
# ## Mapping von Region auf Bezirksnamen

# %%
set_bezirksnamen = set(sorted(df_municipalities['Bezirksname'])) # From Municipality Stammdaten
print(set_bezirksnamen)
print(len(set_bezirksnamen))


# %%
set_regionen = set(sorted(df_cases['Region'])) # From Cases, i.e. the region a case belongs to
print(set_regionen)
print(len(set_regionen))

# %% [markdown]
# The following dictionary is the mapping for the names of the Bezirke from the two different datasources:

# %%
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

# %% [markdown]
# Neue Spalte 'Bezirksname' welche anhand 'Region' gemapped wurde:

# %%
df_cases['Bezirksname'] = df_cases['Region'].apply(lambda region: dict_bezirks_mapping.get(region))
df_cases

# %% [markdown]
#  Nicht gefundene Einträge (z.B. 'ohne Wohnsitz') werden mit None abgefüllt und in einem späteren Schritt mit Kombination aus random und Einwohner auf bekannte Bezirke aufteilt:

# %%
display(df_cases[df_cases['Bezirksname'].isnull()])
print(df_cases[df_cases['Bezirksname'].isnull()].sum())

# %% [markdown]
# ## Assign cases 'ohne Wohnsitz' to known Bezirke
# %% [markdown]
# 'ohne Wohnsitz' cases will be assigned according to the Einwohner of the Bezirke

# %%
df_einwohner_per_bezirk = df_all.groupby(['Bezirksname'])['Einwohner'].sum().reset_index().set_index('Bezirksname')
df_einwohner_per_bezirk['Anteil_Einwohner_an_GR'] = df_einwohner_per_bezirk['Einwohner']/df_einwohner_per_bezirk['Einwohner'].sum()
df_einwohner_per_bezirk


# %%
# Ziel: df_cases
# Source: df_cases[df_cases['Bezirksname'].isnull()]


# %%
df_ohne_wohnsitz = df_cases[df_cases['Bezirksname'].isnull()]
df_ohne_wohnsitz


# %%
lst_bezirke = list(df_einwohner_per_bezirk.index)
lst_bezirke


# %%
lst_anteil_einwohner = list(df_einwohner_per_bezirk['Anteil_Einwohner_an_GR'])
lst_anteil_einwohner


# %%
import numpy as np

# %% [markdown]
# Choose random Bezirke to "inherit" the 'ohne Wohnsitz' cases, but with weights according to Einwohner

# %%
# With choice 1, we choose one Bezrik to inherit all the cases on purpose
df_ohne_wohnsitz['Bezirksname'] = df_ohne_wohnsitz['Bezirksname'].apply(lambda _: np.random.choice(lst_bezirke, 1, p=lst_anteil_einwohner)[0])
df_ohne_wohnsitz


# %%
display(df_ohne_wohnsitz)


# %%
df_cases


# %%
df_cases = df_cases[~df_cases['Bezirksname'].isna()]
df_cases


# %%
df_extended_cases = df_cases.append(df_ohne_wohnsitz)
df_extended_cases


# %%
df_extended_cases = df_extended_cases.groupby(['Datum', 'Bezirksname'])['Neue_Faelle'].sum().reset_index()
df_extended_cases

# %% [markdown]
# ## Merge cases per day and municipality data

# %%
# Get index as column because will be removed after merge
df_all['BFS_Nr'] = df_all.index


# %%
df_municipality_cases = pd.merge(df_all, df_extended_cases, how='inner', left_on='Bezirksname', right_on='Bezirksname')
df_municipality_cases.rename(columns={'Neue_Faelle': 'Neue_Faelle_Region'}, inplace=True)
df_municipality_cases

# %% [markdown]
# ## Distribute Bezirk cases per day to the Gemeinden
# ### use random and Gemeindefläche
# %% [markdown]
# ### Start with Plessur hardcoded
# TODO: Make this dynamic with many loops

# %%
lst_gemeinden_plessur = list(df_all[df_all['Bezirksname'] == 'Plessur'].index)
lst_gemeinden_plessur
#df_municipality_cases['Neue_Faelle_Gemeinde'] = 12


# %%
lst_anteil_flaeche_plessur = [df_all.loc[bfsnr]['Anteil_Flaeche_in_Region'] for bfsnr in lst_gemeinden_plessur]
lst_anteil_flaeche_plessur


# %%
df_plessur_cases = df_municipality_cases[df_municipality_cases['Bezirksname'] == 'Plessur']
df_plessur_cases


# %%
df_plessur_cases[df_plessur_cases['Datum'] == '2020-08-10']


# %%
df_plessur_cases_grouped = df_plessur_cases[['Datum', 'Bezirksname', 'Neue_Faelle_Region']].drop_duplicates()
df_plessur_cases_grouped


# %%
import collections
def get_choices_for_faelle(anzahl_faelle:int):
    # Choose which BFSNrs (aus lst_gemeinden_plessur), get how many of the anzahl_faelle
    random_choices = np.random.choice(lst_gemeinden_plessur, anzahl_faelle, p=lst_anteil_flaeche_plessur)
    # Count the random choices
    counter = collections.Counter(random_choices)
    # Get the number of choices our "current choice" has got
    return counter


# %%
# Datum = 2020-08-10

# calling get_choices_for_faelle does not work, see this example:
display(get_choices_for_faelle(2)) # 3901
display(get_choices_for_faelle(2)) # 3911
display(get_choices_for_faelle(2)) # 3921
display(get_choices_for_faelle(2)) # 3932


# %%
row_date = '2020-08-10'
date_filter = df_plessur_cases['Datum'] == row_date
dict_choices = get_choices_for_faelle(2)
display(dict_choices)
display(df_plessur_cases[date_filter])

# Init with 0 (will be overriden anyways)
# df_plessur_cases['Neue_Faelle_Gemeinde'] = 0

df_faelle_per_gemeinde_row = pd.DataFrame(df_plessur_cases[date_filter]['BFS_Nr'].apply(lambda bfsnr: dict_choices.get(bfsnr, 0)))
df_faelle_per_gemeinde_row.rename(columns={'BFS_Nr': 'Neue_Faelle_Gemeinde'}, inplace=True)
display(df_faelle_per_gemeinde_row)

# TODO: df_plessur_cases here, after a huuuuuge loop


