<p align="center">
  <a href="https://github.com/TabarakoAkula/ChtoZadano">
<picture>
    <img width="300px" height="300px" alt="AChtoZadano" src="https://github.com/user-attachments/assets/559b5c28-5df0-45ba-9c1c-dc9d0a49f516">
</picture>  
</a>
<h1 align="center">
  AChtoZadano
</h1>
<p align="center">
  <i>Convenient interaction with homework for your school</i>
</p>
<div align="center">  
  
  [![master CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml)
  [![server CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml)
  [![bot CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml)  
  [![python - 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10_|_3.11_|_3.12-4b4de3)](https://)
  [![Django - 5.0.6](https://img.shields.io/badge/Django-5.0-4b4de3)](https://)  
  [![Issues](https://img.shields.io/github/license/mashape/apistatus.svg)](https://)
</div>

## 🚀Fast start:
### Requirements:
+ Unix system
+ Python 3.10+
+ Docker && Docker-compose
+ PostgreSQL (rec: 16)
+ Nginx (rec: 1.24.0)
### Clone repository with git
```bash
git clone https://github.com/TabarakoAkula/ChtoZadano.git
```
### Navigate to the project directory
```bash
cd ChtoZadano
```
### Setup ``.env`` file
Fill in the data in ``.env.template`` file  
Rename file to ``.env``:
```bash
mv .env.template .env
```
### Setup ``nginx.conf`` file
Change ``{site_name}`` to IP-address or domain of your site
### Run containers 
```bash
docker compose up --build
```

## ⚙️Local launch
### Requirements:
+ Unix | Windows system
+ Python 3.10+
+ PostgreSQL (rec: 16)
### Clone repository with git
```bash
git clone https://github.com/TabarakoAkula/ChtoZadano.git
```
### Navigate to the project directory
```bash
cd ChtoZadano
```
### Enable virtual environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
Linux:
```bash
python -m venv venv
venv/bin/activate
```
### Install requirements
Production:
```bash
pip install -r requirements/prod.txt
```
Development:
```bash
pip install -r requirements/dev.txt
```
### Setup ``.env`` file
Fill in the data in ``.env.template`` file  
Rename file to ``.env``:
```bash
mv .env.template .env
```
### Create and apply migrations
```bash
cd chtozadano
python manage.py makemigrations
python manage.py migrate
```
### Launch server and bot
```bash
python manage.py runserver
```
```bash
python telegram_bot
```
 
## 👨‍💼Create superuser  
### In production
+ ```bash
  make docker-bash-web
  ```
+ ```bash
  cd chtozadano && python3 manage.py createsuperuser
  ```
### In local launch
+ ```bash
  cd chtozadano
  ```
+ ```bash
  python manage.py createsuperuser
  ```


## 🧾Make scripts:
Some scripts which can make your experience easier  
```bash
make script_name
```
Scripts:
+ ``update``
  + git pull + restart docker a daemon
+ ``docker-rebuildup``
  + docker stop + build + up as daemon
+ ``docker-bash-web``
  + open bash in ``web`` container
+ ``docker-psql``
  + open psql in ``db`` container as user ``posgresql`` 
+ ``docker-clean-all``
  + prune **all** containers
+ ``docker-clean-old``
  + prune ``non-active`` containers
+ ``sort-req``
  + sort all requirements in ``requirements/`` :)

## 🛠️Technical works
In ``.env`` file you can see ``SITE_TECHNICAL_WORKS`` and ``API_TECHNICAL_WORK`` values
### SITE_TECHNICAL_WORKS
If ``True`` - site will be available only for superusers. Other users will see ``templates/technical_works.html`` at any page
### API_TECHNICAL_WOR
If ``True`` - site API will be blocked -> bot will stop working & custom API requests will be unavailable

## The API documentation is in the file <a href="https://github.com/TabarakoAkula/ChtoZadano/blob/814ed9a3d8940f272863eeaae8cc39a04b7fda7c/API.md">API.md</a>