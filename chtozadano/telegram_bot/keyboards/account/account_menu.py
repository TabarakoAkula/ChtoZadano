from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


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
