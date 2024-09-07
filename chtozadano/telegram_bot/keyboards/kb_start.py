from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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


def choose_group_in_kb(
    first_teacher: str,
    second_teacher: str,
) -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text=first_teacher,
                callback_data="ch_group_" + first_teacher.replace(" ", "_"),
            ),
            InlineKeyboardButton(
                text=second_teacher,
                callback_data="ch_group_" + second_teacher.replace(" ", "_"),
            ),
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


def start_become_admin_in_kb() -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text="Да",
                callback_data="start_become_admin_yes",
            ),
            InlineKeyboardButton(
                text="Нет",
                callback_data="start_become_admin_no",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Вернуться в начало",
                callback_data="back_to_start",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)
