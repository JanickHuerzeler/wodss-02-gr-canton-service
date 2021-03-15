# WODSS Gruppe 02 Kantonsservice Graubünden

Kantonsservice für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS). Stellt für den Kanton Graubünden die Corona- sowie Gemeindedaten gemäss API Definition zur Verfügung.



## Prerequisites
- Miniconda
- Python 3.9

Es wird empfohlen, mit einem Conda Environment zu arbeiten.
Folgender Befehler erstellt ein neues Conda Environment mit dem Namen `WODSS`:
``` zsh / CMD
conda create -n WODSS python=3.9
conda env create -f environment.yml
```

Das soeben erstellte Conda Environment muss dabei noch aktiviert werden:
``` zsh /CMD
conda activate WODSS
```
## Build
TODO: FLASK_APP Variable setzen, aktuell via "Play" auf app.py
``` ZSH / CMD
conda activate WODSS
```

## Test

## Installieren von neuen Libraries
Wird eine Library neu installiert, muss diese im `environment.yml` nachgeführt werden.
Dies kann manuell geschehen, am einfachsten durch Kopieren der Ausgabe von folgendem Befehl:
``` zsh / CMD
 conda env export --from-history
```

Sobald das `environment.yml` gepushed wurde, können die Projektmitarbeitenden ihr Environment durch folgenden Befehl auf den aktuellsten Stand bringen, resp. die neue Library auch installieren:

``` zsh / CMD
conda env update --file environment.yml
```
