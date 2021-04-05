# WODSS Gruppe 02 Kantonsservice Graubünden

Kantonsservice für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS). Stellt für den Kanton Graubünden die Corona- sowie Gemeindedaten gemäss API Definition zur Verfügung.


___
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
___
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
___
## Build
TODO: FLASK_APP Variable setzen, aktuell via "Play" auf app.py
``` ZSH / CMD
conda activate WODSS
```
___
## Test
___
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

___
## Live Environment

#### **Domains** ``corona-navigator.ch`` ``gr.corona-navigator.ch``
#### **Deploy latest branch** ``~/deploy.sh``
#### **Git Repo Path** ``/opt/apps/wodss-02-gr-canton-service/``
#### **Restart GR-Service** ``sudo systemctl restart wodss-02-gr-canton-service.service``
___
### Setup Live Server  (SWITCHengines)
#### Step 1 - Install all required APT and PIP packages
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
First we have to open ports 80+443 on SWITCHEngine: https://bit.ly/3fN5UD0
``` ZSH / CMD
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

### Step 8 - Setup SSL
``` ZSH / CMD
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

### Step 9 (optional) - Setup FTP
First we have to open ports 20-21 + 4242-4243 on SWITCHEngine: https://bit.ly/3fN5UD0
``` ZSH / CMD
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

