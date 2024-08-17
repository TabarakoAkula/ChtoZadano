from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


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
