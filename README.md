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
+ AcceptDeclineBecomeAdminAPI:
  + Путь: ``api/v1/become_admin_accept_decline/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``superuser``
  + Суть: принять\отклонить заявку на администратора
  + Действие: при нажатии кнопки принять\отклонить в ``боте``, последний либо меняет статус конкретного пользователя на администратора, либо удаляет запись в таблице ``BecomeAdmin``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``candidate_id`` - ``int`` уникальный ``id`` пользователя-кандидата в телеграм
    + ``decision`` - ``accept``/``decline`` вердикт
  + Возвращает:
      + ``HttpResponse``:
        + ``Это кто? Я такого не знаю``
        + ``Successful accepted``
        + ``Successful declined``
+ ChangeGradeLetterAPI:
  + Путь: ``api/v1/change_grade_letter/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``user``/``superuser``
  + Суть: изменить класс/литеру
  + Действие: при выборе другого класса в ``боте``, последний меняет данные о пользователе в таблице ``Users``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``grade`` - ``int`` класс
    + ``letter`` - ``int`` литера
  + Возвращает:
      + ``HttpResponse``:
        + ``Successful``
+ ChangeChatModeAPI:
  + Путь: ``api/v1/change_chat_mode/`` 
  + Метод: ``GET | POST``
  + ``GET``
    + Ограничение по доступности: ``нет``
    + Суть: изменить получить текущее значение ``chatmode`` у пользователя
    + Действие: при нажатии кнопки в ``боте``, последний возвращает текущее значение ``chatmode``
    + Параметры: 
      + ``api_key`` - ``str`` апи ключ 
      + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + Возвращает:
      + ``HttpResponse``:
        + ``True``/``False``
  + ``POST``
    + Ограничение по доступности: ``нет``
    + Суть: изменить получить текущее значение ``chatmode`` у пользователя
    + Действие: при выборе другого класса в ``боте``, последний меняет ``chatmode`` пользователя в таблице ``Users``
    + Параметры: 
      + ``api_key`` - ``str`` апи ключ 
      + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
      + ``chat_mode`` - ``bool`` новое значение параметра ``chatmode``
    + Возвращает:
      + ``HttpResponse``:
        + ``Successful``

## Homework:
+ ChangeGradeLetterAPI:
  + Путь: ``api/v1/get_last_homework_all_subjects/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``нет``
  + Суть: получить дз последнее по всем предметам
  + Действие: при запросе - возвращает по каждому из предметов последнее дз 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
      + ``JSON``:  
      ``subject``: {  
        ``id``: ``int``,  
        ``grade``: ``int``,  
        ``letter``: ``"str"``,  
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
        ``todo``: ``list``,  
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
      }
+ GetOneSubjectAPI:
  + Путь: ``api/v1/get_homework_for_subject/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``нет``
  + Суть: получить дз последнее по конкретному предмету
  + Действие: при запросе - возвращает последнее дз по отправленному в запросе предмету 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``subject`` - ``str`` название запрашиваемого предмета
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist``
      + ``JSON``:    
        ``id``: ``int``,  
        ``grade``: ``int``,  
        ``letter``: ``"str"``,  
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
        ``todo``: ``list``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
        ``author``: ``str``,  
+ GetAllHomeworkFromDateAPI:
  + Путь: ``api/v1/get_homework_from_date/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``нет``
  + Суть: получить дз за дату
  + Действие: при запросе - возвращает все дз по отправленной в запросе дате 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``date`` - ``datetime`` дата в формате ``yy.mm.dd``
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist``
      + ``JSON``:  
      ``subject``: {  
        ``id``: ``int``,  
        ``grade``: ``int``,  
        ``letter``: ``"str"``,  
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
        ``todo``: ``list``,  
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
      }
+ GetHomeworkFromIdAPI:
  + Путь: ``api/v1/get_homework_from_id/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``нет``
  + Суть: получить дз последнее по его ``id``
  + Действие: при запросе - возвращает дз с указанным ``id`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
  + Возвращает:
      + ``HttpResponse``:
        + ``Undefined``
        + ``Does not exist``
      + ``JSON``:    
        ``id``: ``int``,  
        ``grade``: ``int``,  
        ``letter``: ``"str"``,  
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
        ``todo``: ``list``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
        ``author``: ``str``,  
+ DeleteHomeworkAPI:
  + Путь: ``api/v1/delete_homework/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: удалить дз по его ``id``
  + Действие: при запросе - удаляет дз с указанным ``id`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist``
        + ``Successful``
+ AddHomeWorkAPI:
  + Путь: ``api/v1/add_homework/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: добавить дз
  + Действие: при запросе добавляет изображения, файлы в таблицы ``Images``, ``Files``. И создает с ними запись о домашнем задании в таблице ``Homework`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``subject`` - ``str`` название предмета
    + ``description`` - ``str`` описание домашнего задания
    + ``images`` - ``list`` массив of ``str`` путей к изображениям 
    + ``files`` - ``list`` массив of ``str`` путей к файлам
  + Возвращает:
      + ``HttpResponse``:
        + ``Successful``
+ EditHomeworkDescriptionAPI:
  + Путь: ``api/v1/edit_homework_description/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить описание у домашки
  + Действие: при запросе меняет запись о домашнем задании в таблице ``Homework`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
    + ``description`` - ``str`` описание домашнего задания
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``
+ EditHomeworkImagesAPI:
  + Путь: ``api/v1/edit_homework_images/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить изображения у домашки
  + Действие: при запросе меняет запись о домашнем задании в таблице ``Homework`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
    + ``"images"`` - ``list`` of ``str`` путей к изображениям
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``
+ EditHomeworkFilesAPI:
  + Путь: ``api/v1/edit_homework_files/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить файлы у домашки
  + Действие: при запросе меняет запись о домашнем задании в таблице ``Homework`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
    + ``"files"`` - ``list`` of ``str`` путей к файлам
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``