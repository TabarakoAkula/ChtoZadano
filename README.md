[![master CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/master.yml)
[![server CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/server.yml)
[![bot CI](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml/badge.svg)](https://github.com/TabarakoAkula/ChtoZadano/actions/workflows/bot.yml)

<h1>ChtoZadano</h1>

+ python version: 3.10.x
+ Django version: 5.0.6

Запуск сервера (WGSI, standart):
+ перейдите в директорию ``chtozadano``
+ пропишите в консоли:
  ```bash
  python manage.py runserver
  ```
  
Environments:
+ ``DEBUG`` | True/False
+ ``SECRET_KEY`` | char(256)
+ ``ALLOWED_HOSTS`` | 127.0.0,0.0.0.0,*