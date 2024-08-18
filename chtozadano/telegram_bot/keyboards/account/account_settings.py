from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


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
