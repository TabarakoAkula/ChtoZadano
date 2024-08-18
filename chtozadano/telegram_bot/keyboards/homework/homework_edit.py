from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def to_edit_homework_in_kb(homework_id: int) -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Редактировать✏️",
                callback_data=f"edit_homework_{homework_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )


def edit_homework_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Изменить описание💬",
                callback_data="edit_hw_text",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Удалить запись🗑️",
                callback_data="edit_hw_delete",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Сохранить",
                callback_data="edit_hw_save",
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


def delete_mailing_in_kb() -> InlineKeyboardMarkup:
    buttons_list = [
        [
            InlineKeyboardButton(
                text="Удалить запись🗑️",
                callback_data="delete_mailing",
            ),
        ],
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=buttons_list,
        resize_keyboard=True,
    )
