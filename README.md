# WODSS Gruppe 02 Kantonsservice Graubünden

Kantonsservice für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS). Stellt für den Kanton Graubünden die Corona- sowie Gemeindedaten gemäss API Definition zur Verfügung.

---

## Voraussetzungen

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Python 3.8 (z.B. direkt aus Miniconda)

Es wird empfohlen, mit einem Conda Environment zu arbeiten.
Folgender Befehl erstellt ein neues Conda Environment mit dem Namen `WODSS`:

```zsh / CMD
conda create -n WODSS python=3.8
conda env create -f resources/environment.yml
```

Das soeben erstellte Conda Environment muss dabei noch aktiviert werden:

```zsh /CMD
conda activate WODSS
```

---

## Database

- PostgreSQL installieren
- Datenbank `wodssCantonServiceGR` erstellen
- User `postgres`, Password `postgres` erstellen
- Tabellen erstellen `python manage.py db upgrade`
- Daten für `municipality` Tabelle laden
  - Alternativ: Demodata `resources/demoData.sql`
- Daten für `incidence` Tabelle laden

### Schritt-für-Schritt Anleitung

Nach der Installation von PostgreSQL können folgende Befehle ausgeführt werden:

```ZSH / CMD
createdb wodssCantonServiceGR
psql wodssCantonServiceGR
CREATE USER postgres
```

Zu diesem Zeitpunkt ist die Datenbank und der User erstellt.

Eine neue Verbindung auf die Datenbank kann mit folgendem Befehl geöffnet werden:

```ZSH / CMD
psql -h localhost -d wodssCantonServiceGR -U postgres
```

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

Für die `incidence`-Tabelle muss ein Initial-Import gemacht werden. Folgender Befehl startet den Import via CLI:

```ZSH / CMD
python fetch_incidence.py --full_dataset --save_to_db
```

Für inkrementelle Aktualisierungen (neue Tage einfügen) folgenden Befehl ausführen:

```ZSH / CMD
python fetch_incidence.py --save_to_db
```

Wenn jeweilss `--save_to_db` weggelassen wird, kann ein 'dry-run' ausgeführt werden. Es werden dann alle Schritte bis auf das Schreiben in die DB durchgeführt.

---

## Installieren von neuen Libraries

Wird eine Library neu installiert (`conda install XYZ`), muss diese im `resources/environment.yml` nachgeführt werden.
Dies kann manuell geschehen, am einfachsten durch Kopieren der Ausgabe von folgendem Befehl:

```zsh / CMD
 conda env export --from-history
```

Sobald das `resources/environment.yml` gepushed wurde, können die Projektmitarbeitenden ihr Environment durch folgenden Befehl auf den aktuellsten Stand bringen, resp. die neue Library auch installieren:

```zsh / CMD
conda env update --file resources/environment.yml
```

`--prune` würde zusätzlich noch nicht mehr verwendete Libraries gleich entfernen.

---

## Dev-Environment starten

Nachdem die vorhergehenden Schritte ausgeführt wurden, kann auch der lokale Flask Server gestartet werden:

```CMD/ZSH
python server.py
```

Dieser ist unter [http://localhost:5000](http://localhost:5000) erreichbar. [http://localhost:5000/v1/](http://localhost:5000/v1/) zeigt das Swagger UI an.

---

## Unit Tests

Als Test Framework wird `pytest` verwendet.
Die Unit Tests können mit folgendem Befehl im Hauptverzeichnis ausgeführt werden:

```zsh / CMD
pytest
```

Visual Studio Code bietet einen integrierten Test-Explorer an, der auch pytest unterstützt. Dazu muss die Test Discovery gemäss [Anleitung](https://code.visualstudio.com/docs/python/testing#_test-discovery) eingerichtet werden. Als Test Framework wird logischerweise `pytest` ausgewählt und als Test Directory `tests`.

### Coverage

```zsh / CMD
coverage run -m pytest
```

dann:

```zsh / CMD
coverage report -m
```

oder

```zsh / CMD
coverage html
```

und dann:

Windows

```zsh / CMD
cd htmlcov
start index.html
```

MacOS X

```zsh / CMD
cd htmlcov
open index.html
```

---

## Live Environment

Folgende Übersicht zeigt die wichtigsten URL und Pfade auf dem Live-Server

#### **URLs** `gr.corona-navigator.ch/v1/`

#### **Deploy latest branch** `~/deploy.sh`

#### **Git Repo Path** `/opt/apps/wodss-02-gr-canton-service/`

#### **Restart GR-Service** `sudo systemctl restart wodss-02-gr-canton-service.service`

#### **Conda Env Update** `conda env update --file /opt/apps/wodss-02-gr-canton-service/resources/environment.yml`

---

### Setup Live Server (SWITCHengines)

#### Step 1 - Installieren von benötigten `apt` und `pip` packages

```ZSH / CMD
sudo apt-get update
sudo apt-get install git python3.8-dev python3-pip python3.8 ngnix build-essential postgresql postgresql-contrib
sudo pip3 install uwsgi
```

### Step 2 - Anaconda installieren

```ZSH / CMD
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

```ZSH / CMD
mkdir /opt/apps
cd /opt/apps
git clone https://github.com/JanickHuerzeler/wodss-02-gr-canton-service.git
```

### Step 4 - Virtual Conda Environment erstellen

Weil die bereitgestellte VM zu wenig Arbeitsspeicher hat, wird zuerst ein 2GB Swap-File erstellt

```ZSH / CMD
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
Shorthander:
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

Nun kann die conda env mit Hilfe des environment.yml erstellt werden

```ZSH / CMD
conda env create -f /opt/apps/wodss-02-gr-canton-service/resources/environment.yml

source activate WODSS
```

### Step 5 - Setup PostgreSQL

```ZSH / CMD
sudo -u postgres psql postgres
CREATE DATABASE "wodssCantonServiceGR";
\password postgres (pw: postgres)
\q
cd /opt/apps/wodss-02-gr-canton-service/
/opt/anaconda/envs/WODSS/bin/python3.8 manage.py db upgrade
/opt/anaconda/envs/WODSS/bin/python3.8 fetch_municipality.py --save_to_db
/opt/anaconda/envs/WODSS/bin/python3.8 fetch_incidence.py --full_dataset --save_to_db

sudo systemctl enable postgresql
```

### Step 6 - Setup cronjob (Neue Inzidenzen von GR alle 2 Stunden laden)

```ZSH / CMD
crontab -e
5 */2 * * * cd /opt/apps/wodss-02-gr-canton-service && /opt/anaconda/envs/WODSS/bin/python3.8 fetch_incidence.py --save_to_db
```

Um die Cronjob-Ausführung zu debuggen, kann der Output in eine Datei umgeleitet werden. Dazu dem obigen Befehl `> /tmp/cronjob_fetch_incidency.py.log 2>&1` anfügen.

### Step 7 - Setup Nginx

Die Ports 80 und 443 müssen auf der VM offen sein. SWITCHEngine: https://bit.ly/3fN5UD0
Danach einen vhost in nginx mit folgender Konfiguration erstellen:

```ZSH / CMD
export DOMAIN=corona-navigator.ch

sudo tee /etc/nginx/sites-available/$DOMAIN <<EOF
server {
  listen 80;
  listen [::]:80;
  server_name localhost $DOMAIN www.$DOMAIN;

  root /var/www/html;
  index index.html index.htm;

  location / {
    try_files $uri $uri/ =404;
  }
}
EOF

sudo tee /etc/nginx/sites-available/gr.$DOMAIN <<EOF
server {
  listen 80;
  listen [::]:80;
  server_name localhost gr.$DOMAIN;

  location / {
    proxy_pass http://localhost:5000;
  }
}
EOF

sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
sudo ln -s /etc/nginx/sites-available/gr.$DOMAIN /etc/nginx/sites-enabled/gr.$DOMAIN
sudo systemctl enable nginx
```

### Step 8 - Setup canton service als system service

```ZSH / CMD
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

### Step 9 - Setup SSL

```ZSH / CMD
# Ensure that the version of snapd is up to date
sudo snap install core; sudo snap refresh core

# Install Certbot
sudo snap install --classic certbot

# Prepare the Certbot command
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Confirm plugin containment level
sudo snap set certbot trust-plugin-with-root=ok

# Create Certificate
sudo certbot run -a manual -i nginx -d gr.corona-navigator.ch
sudo certbot run -a manual -i nginx -d corona-navigator.ch -d www.corona-navigator.ch
```

### Deploy Script erstellen

Mit Hilfe dieses Scripts können neue Versionen im Git Repo geholt und auf dem Server ausgerollt werden.

Die Ports 20-21 und 4242-4243 müssen auf der VM offen sein. SWITCHEngine: https://bit.ly/3fN5UD0

```ZSH / CMD
sudo tee /home/ubuntu/deploy.sh <<EOF
echo -e '\nTry to create swapfile...'
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile

echo -e '\nGit fetch & merge...'
cd /opt/apps/wodss-02-gr-canton-service/
git fetch
git reset --hard HEAD > /dev/null
git merge '@{u}'

echo -e '\nUpdate conda environment...'
conda env update --file /opt/apps/wodss-02-gr-canton-service/resources/environment.yml

echo -e '\nUpgrade database...'
cd /opt/apps/wodss-02-gr-canton-service/
/opt/anaconda/envs/WODSS/bin/python3.8 manage.py db upgrade

echo -e '\nRestarting canton service...'
sudo systemctl restart wodss-02-gr-canton-service.service

GREEN='\033[0;32m'
NC='\033[0m' # No Color
printf "\n${GREEN}Deployment successfull${NC}\n\n"
EOF
```

### Step 11 (optional) - Setup FTP

Die Ports 20-21 und 4242-4243 müssen auf der VM offen sein. SWITCHEngine: https://bit.ly/3fN5UD0

```ZSH / CMD
sudo apt-get update
sudo apt install vsftpd
sudo useradd -m ftpuser
sudo passwd ftpuser
sudo systemctl enable vsftpd
sudo vi /etc/vsftp.conf
add following
  write_enable=YES
  pasv_enable=YES
  pasv_addr_resolve=YES
  pasv_address=corona-navigator.ch
  pasv_min_port=4242
  pasv_max_port=4243
```
