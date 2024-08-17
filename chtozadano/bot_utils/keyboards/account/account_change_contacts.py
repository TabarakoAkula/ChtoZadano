from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


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
