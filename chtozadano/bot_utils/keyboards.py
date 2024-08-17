from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def choose_gr_let_in_kb() -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(text="4А", callback_data="ch_gr_let_4А"),
            InlineKeyboardButton(text="4Б", callback_data="ch_gr_let_4Б"),
            InlineKeyboardButton(text="4В", callback_data="ch_gr_let_4В"),
        ],
        [
            InlineKeyboardButton(text="5А", callback_data="ch_gr_let_5А"),
            InlineKeyboardButton(text="5Б", callback_data="ch_gr_let_5Б"),
            InlineKeyboardButton(text="5В", callback_data="ch_gr_let_5В"),
            InlineKeyboardButton(text="5Г", callback_data="ch_gr_let_5Г"),
        ],
        [
            InlineKeyboardButton(text="6А", callback_data="ch_gr_let_6А"),
            InlineKeyboardButton(text="6Б", callback_data="ch_gr_let_6Б"),
            InlineKeyboardButton(text="6В", callback_data="ch_gr_let_6В"),
            InlineKeyboardButton(text="6Г", callback_data="ch_gr_let_6Г"),
        ],
        [
            InlineKeyboardButton(text="7А", callback_data="ch_gr_let_7А"),
            InlineKeyboardButton(text="7Б", callback_data="ch_gr_let_7Б"),
            InlineKeyboardButton(text="7В", callback_data="ch_gr_let_7В"),
        ],
        [
            InlineKeyboardButton(text="8А", callback_data="ch_gr_let_8А"),
            InlineKeyboardButton(text="8Б", callback_data="ch_gr_let_8Б"),
            InlineKeyboardButton(text="8В", callback_data="ch_gr_let_8В"),
        ],
        [
            InlineKeyboardButton(text="9А", callback_data="ch_gr_let_9А"),
            InlineKeyboardButton(text="9Б", callback_data="ch_gr_let_9Б"),
            InlineKeyboardButton(text="9В", callback_data="ch_gr_let_9В"),
        ],
        [
            InlineKeyboardButton(text="10А", callback_data="ch_gr_let_10А"),
            InlineKeyboardButton(text="10Б", callback_data="ch_gr_let_10Б"),
            InlineKeyboardButton(text="10В", callback_data="ch_gr_let_10В"),
        ],
        [
            InlineKeyboardButton(text="11А", callback_data="ch_gr_let_11А"),
            InlineKeyboardButton(text="11Б", callback_data="ch_gr_let_11Б"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def choose_group_in_kb() -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(text="1", callback_data="ch_group_1"),
            InlineKeyboardButton(text="2", callback_data="ch_group_2"),
        ],
        [
            InlineKeyboardButton(
                text="Вернуться",
                callback_data="back_to_start",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def open_site_in_kb(domain) -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text="Открыть сайт",
                url=domain + "/user/sign_in/",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def menu_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Расписание🗓"),
            KeyboardButton(text="Домашка📝"),
            KeyboardButton(text="Аккаунт👤"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def schedule_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="На неделю"),
            KeyboardButton(text="На завтра"),
        ],
        [
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def account_user_page_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Имя и Фамилия✏️"),
            KeyboardButton(text="Сменить класс🏫"),
        ],
        [
            KeyboardButton(text="Стать администратором👨‍💼"),
            KeyboardButton(text="Настройки🛠️"),
        ],
        [
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def account_admin_page_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Имя и Фамилия✏️"),
            KeyboardButton(text="Сменить класс🏫"),
        ],
        [
            KeyboardButton(text="Настройки🛠️"),
        ],
        [
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def change_contacts_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Изменить данные📝"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def become_admin_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Отправить заявку📁"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def show_become_admin_in_kb(user_id) -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text="Принять✅",
                callback_data=f"decision_show_become_admin_accept_{user_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить❌",
                callback_data=f"decision_show_become_admin_decline_{user_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def settings_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Сменить режим чата💬"),
            KeyboardButton(text="Сменить режим цитат📓"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def homework_main_admin_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Домашка на завтра⏰"),
            KeyboardButton(text="Выбрать предмет📚"),
        ],
        [
            KeyboardButton(text="Добавить📋"),
            KeyboardButton(text="Найти домашку🔎"),
        ],
        [
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def homework_main_user_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Домашка на завтра⏰"),
            KeyboardButton(text="Выбрать предмет📚"),
        ],
        [
            KeyboardButton(text="Найти домашку🔎"),
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def homework_subject_in_kb(subjects: list, add: bool) -> InlineKeyboardMarkup:
    inline_list = []
    counter = 1
    temp_list = []
    last_subject = subjects[-1]
    for i in subjects:
        i = i[0].upper() + i[1:]
        if add:
            temp_list.append(
                InlineKeyboardButton(
                    text=i,
                    callback_data=f"add_hw_subject_{i}",
                ),
            )
        else:
            temp_list.append(
                InlineKeyboardButton(
                    text=i,
                    callback_data=f"homework_subject_{i}",
                ),
            )
        if counter % 2 == 0 and i != last_subject:
            inline_list.append(temp_list)
            temp_list = []
        elif i.lower() == last_subject:
            inline_list.append(temp_list)
        counter += 1
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def get_mailings() -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text="Информация для школы",
                callback_data="add_hw_subject_schoolinfo",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Информация для админов",
                callback_data="add_hw_subject_adminsinfo",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def add_homework_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Опубликовать🚀",
                callback_data="publish_hw",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Добавить файлы📂",
                callback_data="add_homework_files",
            ),
            InlineKeyboardButton(
                text="Сбросить❌",
                callback_data="back_to_menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )


def return_to_menu() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(
                text="Вернуться",
                callback_data="back_to_menu",
            ),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons_list,
        resize_keyboard=True,
    )


def add_homework_maximum_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Опубликовать🚀",
                callback_data="publish_hw",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Сбросить❌",
                callback_data="back_to_menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )


def to_edit_homework_in_kb(homework_id: int) -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Редактировать✏️",
                callback_data=f"edit_homework_{homework_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )


def edit_homework_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Изменить описание💬",
                callback_data="edit_hw_text",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Удалить запись🗑️",
                callback_data="edit_hw_delete",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Сохранить",
                callback_data="edit_hw_save",
            ),
            InlineKeyboardButton(
                text="Сбросить❌",
                callback_data="back_to_menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )


def delete_mailing_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Удалить запись🗑️",
                callback_data="delete_mailing",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )
