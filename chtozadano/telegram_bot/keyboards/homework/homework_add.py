from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


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
