from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


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


def return_to_homework_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [[KeyboardButton(text="Назад")]]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)
