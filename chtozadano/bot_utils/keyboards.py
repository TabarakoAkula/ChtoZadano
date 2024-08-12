from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def choose_gr_let_in_kb():
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


def choose_group_in_kb():
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


def open_site_in_kb(domain):
    inline_list = [
        [
            InlineKeyboardButton(
                text="Открыть сайт",
                url=domain + "/user/sign_in/",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)


def menu_rp_kb():
    buttons_list = [
        [
            KeyboardButton(text="Расписание🗓"),
            KeyboardButton(text="Домашка📝"),
            KeyboardButton(text="Аккаунт👤"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def schedule_rp_kb():
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


def account_user_page_rp_kb():
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


def account_admin_page_rp_kb():
    buttons_list = [
        [
            KeyboardButton(text="Имя и Фамилия✏️"),
            KeyboardButton(text="Сменить класс🏫"),
        ],
        [
            KeyboardButton(text="Настройки🛠️"),
            KeyboardButton(text="Вернуться"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def change_contacts_rp_kb():
    buttons_list = [
        [
            KeyboardButton(text="Изменить данные📝"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def become_admin_rp_kb():
    buttons_list = [
        [
            KeyboardButton(text="Отправить заявку📁"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)
