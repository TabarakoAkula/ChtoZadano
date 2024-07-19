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
  + Действие: отправляет запрос на сервер для создания записи в таблице ``SignIn``, данные в которой будут использованы при входе/регистрации
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
    + Действие: возвращает с сервера все заявки на становление администратором с таблички ``BecomeAdmin``
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
    + Действие: отправляет на сервер запрос, данные из которого записываются в табличку ``BecomeAdmin`` 
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
  + Действие: меняет статус конкретного пользователя на администратора и/или удаляет запись на становление в таблице ``BecomeAdmin``
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
  + Действие: по запросу меняет данные о пользователе в таблице ``Users``
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
    + Действие: возвращает текущее значение ``chatmode``
    + Параметры: 
      + ``api_key`` - ``str`` апи ключ 
      + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + Возвращает:
      + ``HttpResponse``:
        + ``True``/``False``
  + ``POST``
    + Ограничение по доступности: ``нет``
    + Суть: изменить получить текущее значение ``chatmode`` у пользователя
    + Действие: отправляет запрос на изменение ``chatmode`` пользователя в таблице ``Users``
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
  + Действие: возвращает последнее дз по отправленному в запросе предмету 
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
  + Действие: возвращает все дз по отправленной в запросе дате 
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
  + Действие: возвращает дз с указанным ``id`` 
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
  + Действие: удаляет дз с указанным ``id`` 
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
+ GetMailingAPI:
  + Путь: ``api/v1/get_mailing/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``зависящая``
  + Суть: получить все ``Mailing``'и
  + Действие: возвращает подходящие по уровню ``Mailing`` из: ``School``, ``Class``, ``Admin``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
      + ``JSON``:
      ``level``: {  
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
+ AddMailingAPI:
  + Путь: ``api/v1/add_mailing/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``зависящая``
  + Суть: добавить ``Mailing``'
  + Действие: добавляет ``Mailing`` в таблицу ``Homework`` с соответствующим уровнем
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``level`` - уровень оповещения ``school``/``admins``/``class``
    + ``description`` - описание оповещения
    + ``images`` - ``list`` of ``str`` путей к изображениям
    + ``files`` - ``list`` of ``str`` путей к файлам
  + Возвращает:
      + ``HttpResponse``:
        + ``Successful``
+ EditMailingAPI:
  + Путь: ``api/v1/edit_mailing/`` 
  + Метод: ``GET``
  + Ограничение по доступности: ``зависящая``
  + Суть: посмотреть какой ``Mailing`` будет изменен
  + Действие: возвращает ``Mailing`` по его ``homework_id``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id ``Mailing``'а
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
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,
+ EditMailingDescriptionAPI:
  + Путь: ``api/v1/edit_mailing_description/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить описание у рассылки
  + Действие: при запросе меняет запись о рассылке в таблице ``Homework`` 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id рассылки
    + ``description`` - ``str`` описание домашнего задания
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``
        + ``Error``
+ EditMailingImagesAPI:
  + Путь: ``api/v1/edit_mailing_images/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить изображения у рассылки
  + Действие: при запросе меняет изображения связанные с указанной рассылкой 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id рассылки
    + ``"images"`` - ``list`` of ``str`` путей к изображениям
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``
+ EditMailingFilesAPI:
  + Путь: ``api/v1/edit_mailing_files/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: изменить файлы у рассылки
  + Действие: при запросе меняет файлы связанные с указанной рассылкой 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id рассылки
    + ``"files"`` - ``list`` of ``str`` путей к файлам
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``
+ DeleteMailingAPI:
  + Путь: ``api/v1/delete_mailing/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``staff``/``superuser``
  + Суть: удалить рассылку
  + Действие: удаляет запись о рассылке, а также все связанные изображения и файлы
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id рассылки
  + Возвращает:
      + ``HttpResponse``:
        + ``Does not exist`` 
        + ``Successful``