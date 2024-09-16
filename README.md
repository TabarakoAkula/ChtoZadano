<p align="center">
  <a href="https://github.com/TabarakoAkula/ChtoZadano">
<picture>
    <img alt="AChtoZadano" src="./chtozadano/static_dev/img/panel_logo.jpg">
</picture>  
</a>
<h1 align="center">
  AChtoZadano
</h1>
<p align="center">
  <i>Convenient interaction with homework for your school</i>
</p>
<div align="center">  
  
  [![Django tests](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/django-tests.yml/badge.svg?branch=master)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/django-tests.yml)
  [![Docker build](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/docker-build.yml/badge.svg?branch=master)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/docker-build.yml)
  [![Linters](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/linters-check.yml/badge.svg?branch=master)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/linters-check.yml)  
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
### Collect static files
```bash
python manage.py collectstatic
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

## 📟Admin panel
The site allows you to work with database through its admin panel. 
To enter it, you need to:
+ Create superuser
+ Go to the address ``/admin/`` and enter superuser data
#### OR
+ Go to ``/user/account/``, press ``Админ панель`` and enter superuser data  

## 📁Data customization
If you want to upload another data about teachers/subjects/group - change data in this files:
### .Py 
#### ``chtozadano/chtozadano/settings.py``:
+ ``LANGUAGE_CODE``: ``str`` - Select language code for your site server (Internationalization is under development, see #119) 
+ ``TIME_ZONE``: ``str`` - Select in which timezone will be working server (``USE_TZ`` must be enabled)
+ ``USE_TZ``: ``bool`` - Use timezone time instead of server time (**BE CAREFUL** It can ruin adding rows to db)
+ ``DATA_UPLOAD_MAX_MEMORY_SIZE``: ``int`` - Choose maximum data size to upload to site per request (Change this value in ``nginx.conf`` too)
+ ``FILE_UPLOAD_MAX_MEMORY_SIZE``: ``int`` - Choose file data size to upload to site per request (Change this value in ``nginx.conf`` too)
#### ``chtozadano/gunicorn_congig.py``:
+ ``workers``: ``int`` - set number of workers that will serve your site (formula: (2 * number_of_cors) + 1
+ ``loglevel``: ``str`` set loglevel for gunicorn (Saving in ``chtozadano/logs/gunicorn_access.log|gunicorn_errors.log)

### JSON
+ ``/chtozadano/static_dev/json/subjects.json``
+ ``/chtozadano/static_dev/json/grades_subjects.json``
+ ``/chtozadano/static_dev/json/eng_teachers.json``
### Models
``/chtozadano/users/models.py``:  
+ ``GRADE_CHOICES``  
+ ``LETTER_CHOICES``  

``/chtozadano/homework/models.py``:  
+ ``GRADE_CHOICES``  
+ ``LETTER_CHOICES``

``/chtozadano/homework/forms.py``:  
+ ``GROUP_CHOICES``  
### HTML
``/chtozadano/templates/users/sign_in.html``
+ ``line 15`` - href to bot

``/chtozadano/templates/users/sign_up.html``
+ ``line 16`` - href to bot

### Nginx
#### ``nginx.conf`` file:
+ ``{site_name}`` - IP address or domain name to be redirected (+ Redirecting from http to https)
+ ``client_max_body_size`` - Choose maximum data size to upload to server per request

## 📆Adding schedule
You can fast upload your schedule using script in ``/chtozadano/scripts/add_schedule_script.py``
### Fill data
Fill file ``/chtozadano/scripts/timetable.csv`` according to the template:
+ ``grade`` (f.e. ``10А``)
+ lessons in format ``weekday``_``lesson``, where 0 - Monday (f.e. ``1_2`` = ``Thuesday_Second lesson``)
+ Determine the maximum number of lessons and specify it for each day of the week!
If the maximum number of lessons is 4, then the headers will look like this: ``grades;0_1;0_2;0_3;0_4;1_1;1_2;1_3;1_4....``
### Preparation
There are come required fields:
+ Request url - ``DOMAIN_URL`` (``.env``file)
+ Superuser id - ``SUPERUSER_ID`` (``.env`` file)
+ Api key - ``API_KEY`` (``.env`` file)

If you want you can change:
+ Filename - ``FILENAME`` (``script`` file)
+ CSV delimiter - ``DELIMITER`` (``script`` file)
+ CSV encoding format - ``ENCONDING`` (``script`` file)

### Launch
+ Go to ``/chtozadano/scripts`` directory
+ Launch ``script`` file
  ```bash
  python add_schedule_script.py
  ```

## 🖨️Logging
Project allows ability to log data into files and console.
### Server
+ ``console`` logs
+ ``telegram bots`` - some functions (ex. ``DeleteOldHomework``) will notify superusers using messages from the bot
+ ``chtozadano/logs/django.log``
+ ``chtozadano/logs/gunicorn_access.log``
+ ``chtozadano/logs/gunicorn_errors.log``
### Other services | containers:
+ ``console`` logs


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

## 📎Redis & Celery
``AChtoZadano`` allows to use caching using Redis as well as scheduling tasks using Celery (Celery worker and Celery beat).
The support is already initially enabled in docker containers, but if you want to configure it,
you should change the following parameters:
### In ``.env`` file:
+ ``USE_REDIS``: ``bool`` - Toggle using Redis 
+ ``REDIS_SITE_URL``: ``str`` - URL to Redis database for Site cache
+ ``REDIS_BOT_URL``: ``str`` - URL to Redis database for Bot cache
+ ``USE_CELERY``: ``bool`` - Toggle using Celery(``USE_REDIS`` must be ``True``)
+ ``CELERY_BROKER_URL``: ``str`` - URL to Redis database for Celery tasks
### In ``chtozadano/celery_app`` file:
+ ``timezone``: str - select timezone where will work your Celery scheduler (ex. ``app.conf.timezone = "Europe/Moscow"``)

## API
#### API documentation is in the file <a href="./API.md">API.md</a>
