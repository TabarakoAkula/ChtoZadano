
# Документация по API:
<details><summary><h2>Users:</h2></summary>
  
+ CodeConfirmationAPI:
  + Путь: ``api/v1/code_confirmation/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить код для входа в систему
  + Действие: отправляет запрос на сервер для создания записи в таблице ``SignIn``, данные в которой будут использованы при входе/регистрации
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя в телеграм
    + ``confirmation_code`` - ``int`` 6и значный код идентификации, который был выдан пользователю
    + ``name`` - ``str``  текущее имя пользователя в Telegram
  + Возвращает:
    + ``HttpResponse``: ``Информация о пользователе {telegram_id} успешно внесена в таблицу SignIN``  
+ CreateUserAPI:
  + Путь: ``api/v1/create_user/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: создать аккаунт
  + Действие: отправляет запрос на сервер для создания записи в таблицах ``auth.user`` и ``users.user``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя в телеграм
    + ``name`` - ``str``  текущее имя пользователя в Telegram
    + ``grade`` - ``int`` номера класса
    + ``letter`` - ``str`` литера класса
    + ``group`` - ``int`` группа класса
  + Возвращает:
    + ``HttpResponse``:
      + ``Successful``
      + ``Пользователь уже существует``  
+ GetContactsAPI:  
  + Путь: ``api/v1/get_contacts/``  
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить текущие имя и фамилию пользователя
  + Действие: возвращает ``first_name`` и ``last_name`` указанного пользователя
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
  + ``JSON``:  
  + ``first_name``: ``str``  
  + ``last_name``: ``str``  
  + ``POST``  
+ ChangeContactsAPI:  
  + Путь: ``api/v1/change_contacts/``   
  + Метод: ``POST``  
  + Ограничение по доступности: ``нет``
  + Суть: изменить имя и фамилию текущего пользователя
  + Действие: изменяет ``first_name`` и ``last_name`` указанного пользователя
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + ``first_name`` - ``str`` новое имя пользователя 
  + ``last_name`` - ``str`` новая фамилия пользователя
  + Возвращает:
  + ``HttpResponse``:
  + ``Successful``
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
+ GetChatModeAPI:
  + Путь: ``api/v1/get_chat_mode/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить текущее значение ``chatmode`` у пользователя
  + Действие: возвращает текущее значение ``chatmode``
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
  + ``JSON``:  
    ``chat_mode`` - ``bool``  
+ ChangeChatModeAPI:
  + Путь: ``api/v1/change_chat_mode/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: изменить текущее значение ``chatmode`` у пользователя
  + Действие: отправляет запрос на изменение ``chatmode`` пользователя в таблице ``Users``
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
  + ``JSON``:  
    ``chat_mode`` - ``bool``  
+ GetQuotesAPI:
  + Путь: ``api/v1/get_quotes_status/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить текущее значение ``show_quotes`` у пользователя
  + Действие: возвращает текущее значение ``show_quotes``
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
  + ``JSON``:  
    ``quotes_status`` - ``bool``  
+ ChangeQuotesAPI:
  + Путь: ``api/v1/change_quotes/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: изменить текущее значение ``show_quotes`` у пользователя
  + Действие: отправляет запрос на изменение ``show_quotes`` пользователя в таблице ``Users``
  + Параметры: 
  + ``api_key`` - ``str`` апи ключ 
  + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
  + ``JSON``:  
    ``quotes_status`` - ``bool``  
+ ShowBecomeAdminAPI:
  + Путь: ``api/v1/show_become_admin/`` 
  + Метод: ``POST``
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
+ BecomeAdminAPI:
  + Путь: ``api/v1/become_admin/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: отправить заявку на становление администратором
  + Действие: отправляет на сервер запрос, данные из которого записываются в табличку ``BecomeAdmin`` 
  + Параметры: 
  + ``api_key`` - апи ключ 
  + ``telegram_id`` - уникальный ``id`` пользователя в телеграм
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
    + ``decision`` - ``accept``/``decline`` вердикт
  + Возвращает:
      + ``HttpResponse``:
        + ``Это кто? Я такого не знаю``
        + ``Successful accepted``
        + ``Successful declined``
+ IsUserInSystemAPI:
  + Путь: ``api/v1/is_user_in_system/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: узнать есть ли пользователь в системе
  + Действие: пытается получить пользователя по его ``telegram_id``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ  
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм  
  + Возвращает:  
      + ``HttpResponse``:  
        + ``True``/``False``  
+ GetAdminsAPI:
  + Путь: ``api/v1/get_admins/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: узнать кто в твоём классе админ
  + Действие: получает из ``Users`` данные о пользователях-администраторах
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ  
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм 
  + Возвращает:  
      + ``JSON``:  
        + ``list`` of dictionaries with:  
      ``telegram_id`` - ``int``  
      ``group`` - ``int``  
      ``user``: {  
        ``first_name`` - ``str``  
        ``last_name`` - ``str``  
        }  
+ IsUserAdminAPI:
  + Путь: ``api/v1/is_user_admin/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: узнать права пользователя
  + Действие: получает из ``Users.user`` данные о статусе пользователя
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ  
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм 
  + Возвращает:  
      + ``JSON``:   
      ``is_admin`` - ``bool``  
      ``is_superuser`` - ``bool``  
</details>
<details><summary><h2>Homework:</h2></summary>

+ GetLastHomeworkAllSubjectsAPI:
  + Путь: ``api/v1/get_last_homework_all_subjects/`` 
  + Метод: ``POST``
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
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``int``,  
        ``created_at``: ``datetime``,  
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
      }
+ GetOneSubjectAPI:
  + Путь: ``api/v1/get_homework_for_subject/`` 
  + Метод: ``POST``
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
        ``description``: ``str``,  
        ``subject``: ``"str"``,
        ``group``: ``int``,  
        ``created_at``: ``datetime``,
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
+ GetAllHomeworkFromDateAPI:
  + Путь: ``api/v1/get_homework_from_date/`` 
  + Метод: ``POST``
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
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
      }
+ GetHomeworkFromIdAPI:
  + Путь: ``api/v1/get_homework_from_id/`` 
  + Метод: ``POST``
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
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
        ``author``: ``str``,  
        ``images``: ``list``,   
        ``files``: ``list``,  
+ GetTomorrowHomeworkAPI:
  + Путь: ``api/v1/get_tomorrow_homework/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить дз на следующий день
  + Действие: получает последнюю домашку по каждому предмету **завтра** (по расписанию)
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
  + Возвращает:
      + ``JSON``:  
        ``lesson``: {  
          ``id``: ``int``,
          ``description``: ``str``,  
          ``subject``: ``"str"``,  
          ``group``: ``"int"``,  
          ``created_at``: ``datetime``,
          ``author``: ``str``,  
          ``images``: ``list``,   
          ``files``: ``list``,  
          ``data``: ``boolean``,  
        }  
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
+ GetMailingAPI:
  + Путь: ``api/v1/get_mailing/`` 
  + Метод: ``POST``
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
        ``description``: ``str``,  
        ``subject``: ``"str"``,  
        ``group``: ``"int"``,  
        ``created_at``: ``datetime``,  
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
  + Метод: ``POST``
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
+ TodoWorkAPI:
  + Путь: ``api/v1/change_todo/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: отметить домашнее задание выполненным/невыполненным
  + Действие: меняет у заданного домашнего задания значение ``is_done`` на обратное
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``homework_id`` - ``int`` id домашки
  + Возвращает:
      + ``HttpResponse``:
        + ``Successful``
+ GetTomorrowScheduleAPI:
  + Путь: ``api/v1/get_tomorrow_schedule/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить расписание на завтра
  + Действие: возвращает расписанию на завтрашнюю дату с метода в ``utils``
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
      + ``JSON``:
        + ``list`` if ``dict`` with:  
          ``weekday`` - ``int``  
          ``lesson`` - ``int``  
          ``subject`` - ``str``  
+ DeleteOldHomeworkAPI:
  + Путь: ``api/v1/delete_old_homework/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``superuser``
  + Суть: удалить старое дз
  + Действие: удаляет все домашки и связанные с ними изображения и файлы, которым более 14 дней  
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
      + ``HttpResponse``
        + ``Successful delete {todo_d_counter:int} Todo and {homework_d_counter:int} Homework rows``
+ AddScheduleAPI:
  + Путь: ``api/v1/add_schedule/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``superuser``
  + Суть: добавить расписание
  + Действие: добавляет в таблицу ``Schedule`` новую запись 
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
    + ``grade`` - ``int`` класс
    + ``letter`` - ``str`` литера
    + ``group`` - ``int`` группа
    + ``weekday`` - ``int`` день недели
    + ``lesson`` - ``int`` номер урока
    + ``subject`` - ``str`` аббревиатура предмета
  + Возвращает:
      + ``HttpResponse``
        + ``Successful``  
+ GetWeekSchedule:
  + Путь: ``api/v1/get_week_schedule/`` 
  + Метод: ``POST``
  + Ограничение по доступности: ``нет``
  + Суть: получить расписание на всю неделю
  + Действие: забирает с таблицы ``Schedule`` все подходящие  
  + Параметры: 
    + ``api_key`` - ``str`` апи ключ 
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:
      + ``JSON``
        + ``list`` if ``dicts`` with:
          ``weekday`` - ``int`` день недели 
          ``lesson`` - ``int``  номер урока
          ``subject`` - ``str`` название предмета
+ GetUserSubjects:
  + Путь: ``api/v1/get_user_subjects/``   
  + Метод: ``POST``  
  + Ограничение по доступности: ``нет``    
  + Суть: получить все предметы пользователя  
  + Действие: забирает с ``homework.utils`` данные о предметах пользователя      
  + Параметры:   
    + ``api_key`` - ``str`` апи ключ   
    + ``telegram_id`` - ``int`` уникальный ``id`` пользователя-отправителя в телеграм
  + Возвращает:  
      + ``JSON``  
        + ``list`` with:  
          ``subject_name`` - ``str`` название предмет  
</details>
