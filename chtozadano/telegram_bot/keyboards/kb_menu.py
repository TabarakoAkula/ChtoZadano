from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def menu_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Расписание🗓"),
            KeyboardButton(text="Домашка📝"),
            KeyboardButton(text="Аккаунт👤"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)
