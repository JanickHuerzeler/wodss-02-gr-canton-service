# WODSS Gruppe 02 Kantonsservice Graubünden

Kantonsservice für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS). Stellt für den Kanton Graubünden die Corona- sowie Gemeindedaten gemäss API Definition zur Verfügung.



## Prerequisites
- Miniconda
- Python 3.9

Es wird empfohlen, mit einem Conda Environment zu arbeiten.
Folgender Befehler erstellt ein neues Conda Environment mit dem Namen `WODSS`:
``` zsh / CMD
conda create -n WODSS python=3.9
conda env create -f resources/environment.yml
```

Das soeben erstellte Conda Environment muss dabei noch aktiviert werden:
``` zsh /CMD
conda activate WODSS
```

## Database
- Install PostgreSQL
- Create database `wodssCantonServiceGR`
- User `postgres`, Password `postgres`
- Create tables `python manage.py db upgrade`
- Load table `municipality`
    - Alternatively: Demodata `resources/demoData.sql`

### Schritt-für-Schritt Anleitung
Nach der Installation von PostgreSQL können folgende Befehle ausgeführt werden:
``` ZSH / CMD
createdb wodssCantonServiceGR
psql wodssCantonServiceGR
CREATE USER postgres 
```

Zu diesem Zeitpunkt ist die Datenbank und der User erstellt.

In einem neuen Terminal/Konsole sollen nun die Tabellen aufgrund der Model-Klassen in Python erstellt werden:

Falls DB neu erstellt werden soll:
```ZSH / CMD
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

Ansonsten, falls nur aktualisiert werden soll: 
```ZSH / CMD
python manage.py db upgrade
```

Die `municipality`-Tabelle muss einmalig abgefüllt werden. Folgender Befehl startet den Import via CLI:
```ZSH / CMD
python fetch_municipality.py --save_to_db
```

## Build
TODO: FLASK_APP Variable setzen, aktuell via "Play" auf app.py
``` ZSH / CMD
conda activate WODSS
```

## Test

## Installieren von neuen Libraries
Wird eine Library neu installiert (`conda install XYZ`), muss diese im `resources/environment.yml` nachgeführt werden.
Dies kann manuell geschehen, am einfachsten durch Kopieren der Ausgabe von folgendem Befehl:
``` zsh / CMD
 conda env export --from-history
```

Sobald das `resources/environment.yml` gepushed wurde, können die Projektmitarbeitenden ihr Environment durch folgenden Befehl auf den aktuellsten Stand bringen, resp. die neue Library auch installieren:

``` zsh / CMD
conda env update --file resources/environment.yml
```

`--prune` würde zusätzlich noch nicht mehr verwendete Libraries gleich entfernen.

## Unit Tests
Die Unit Tests können mit folgendem Befehl im Hauptverzeichnis ausgeführt werden:

``` zsh / CMD
pytest
```

### Coverage
``` zsh / CMD
coverage run -m pytest
```
oder
``` zsh / CMD
coverage report -m
```
oder
``` zsh / CMD
coverage html
```
und dann: 

Windows
``` zsh / CMD
cd htmlcov
start index.html
```
MacOS X
``` zsh / CMD
cd htmlcov
open index.html
```



## Setup Live Environment (SWITCHengines)

### Step 1 - Install all required APT and PIP packages
``` ZSH / CMD
sudo apt-get update
sudo apt-get install git python-dev python3-pip ngnix build-essential postgresql postgresql-contrib
sudo pip3 install uwsgi
```

### Step 2 - Install Anaconda
``` ZSH / CMD
sudo mkdir -p /opt
sudo chown $USER /opt
mkdir /opt/anaconda
cd /opt/anaconda/
wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
bash Anaconda3-2020.11-Linux-x86_64.sh -u -b -p /opt/anaconda
rm Anaconda3-2020.11-Linux-x86_64.sh
export PATH=/opt/anaconda/bin:$PATH
source /etc/environment && export PATH
```

### Step 3 - Clone Git Repository
``` ZSH / CMD
mkdir /opt/apps
cd /opt/apps
git clone https://github.com/JanickHuerzeler/wodss-02-gr-canton-service.git
```

### Step 4 - Create Virtual Conda Environment
Because the virtual machine has insufficient memory, we first have to create a temporary 2GB swapfile
``` ZSH / CMD
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```
Now we can create the conda env using environment.yml 
``` ZSH / CMD
conda env create -f /opt/apps/wodss-02-gr-canton-service/resources/environment.yml
source activate WODSS
```

### Step 5 - Setup PostgreSQL
``` ZSH / CMD
sudo -u postgres psql postgres
CREATE DATABASE wodssCantonServiceGR;
\password postgres (pw: postgres)
\q
cd /opt/apps/wodss-02-gr-canton-service
python3 manage.py db upgrade

sudo systemctl enable postgresql
```

### Step 6 - Setup Nginx
First we have to open ports 80+443 on SWITCHEngines: https://bit.ly/3fN5UD0
``` ZSH / CMD
export DOMAIN=gr.corona-navigator.ch
sudo tee /etc/nginx/sites-available/$DOMAIN <<EOF
server {
  listen 80;
  listen [::]:80;
  server_name localhost gr.corona-navigator.ch;

  location / {
    proxy_pass http://localhost:5000;
  }
}
EOF

sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
sudo systemctl enable nginx
```
### Step 7 - Setup canton service as a system service
``` ZSH / CMD
sudo tee /etc/systemd/system/wodss-02-gr-canton-service.service << EOF
[Unit]
Description=uWSGI instance to serve wodss-02-gr-canton-service

[Service]
ExecStart=/bin/bash -c 'cd /opt/apps/wodss-02-gr-canton-service && uwsgi -H /opt/anaconda/envs/WODSS resources/uwsgi.ini'

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable wodss-02-gr-canton-service
```
