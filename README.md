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
  
# Документация по API:
## Users:
+ CodeConfirmationAPI:
  + Путь: ``api/v1/code_confirmation/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить код для входа в систему
  + Действие: при просьбе получение кода в ``боте``, последний отправляет запрос на сервер для создания записи в таблице ``SignIn``, данные в которой будут использованы при входе/регистрации
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя в телеграм
    + ``confirmation_code`` - ``int`` 6и значный код подтверждения, который был выдан пользователю
    + ``name`` - ``str``  текущее имя пользователя в Telegram
  + Возвращает:
    + ``HttpResponse``: ``Информация о пользователе {telegram_id} успешно внесена в таблицу SignIN``
+ BecomeAdminAPI:
  + Путь: ``api/v1/become_admin/`` 
  + Метод: ``GET | POST``
  + ``GET``
    + Ограничение по доступности: ``superuser``
    + Суть: получить все заявки на становление администратором
    + Действие: по запросу в ``боте``, последний возвращает с сервера все заявки на становление администратором 
    + Параметры: 
      + ``api_key`` - ``str`` апи ключ 
      + ``telegram_id`` - ``int`` уникальный ``id`` пользователя в телеграм
    + Возвращает: 
      + ``JSON`` list of dictionaries with:  
      ``id``: ``int``,  
      ``grade``: ``int``,  
      ``letter``: ``"str"``,  
      ``group``: ``int``,  
      ``first_name``: ``"str"``,  
      ``last_name``: ``"str"``,  
      ``telegram_id``: ``int``
  + ``POST``
    + Ограничение по доступности: ``нет``
    + Суть: отправить заявку на становление администратором
    + Действие: по запросу из ``боте``, последний отправляет на сервер запрос, данные из которого записываются в табличку ``BecomeAdmin`` 
    + Параметры: 
      + ``api_key`` - апи ключ 
      + ``telegram_id`` - уникальный ``id`` пользователя в телеграм
      + ``grade`` - ``int`` номер класса
      + ``letter`` - ``str`` литера класса
      + ``group`` - ``int`` группа в классе  
      + ``first_name`` - ``str`` имя
      + ``last_name`` - ``str`` фамилия
    + Возвращает: 
      + ``HttpResponse``:
        + ``You are already admin``
        + ``You are superuser, damn``
        + ``Already have request``
        + ``Successful``
        + ``Wait pls``
+ ### IN PROGRESS
## Homework:
+ ### IN PROGRESS