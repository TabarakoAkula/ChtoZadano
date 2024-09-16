from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def choose_gr_let_in_kb(classes: dict) -> InlineKeyboardMarkup:
    inline_list = []
    for grade in classes:
        letters = classes[grade]
        buttons_list = []
        for letter_button in letters:
            grade_name = grade + letter_button
            buttons_list.append(
                InlineKeyboardButton(
                    text=grade_name,
                    callback_data="ch_gr_let_" + grade_name),
            )
        inline_list.append(buttons_list)
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
