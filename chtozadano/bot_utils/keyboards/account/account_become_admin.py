from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def become_admin_rp_kb() -> ReplyKeyboardMarkup:
    buttons_list = [
        [
            KeyboardButton(text="Отправить заявку📁"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons_list, resize_keyboard=True)


def show_become_admin_in_kb(user_id) -> InlineKeyboardMarkup:
    inline_list = [
        [
            InlineKeyboardButton(
                text="Принять✅",
                callback_data=f"decision_show_become_admin_accept_{user_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить❌",
                callback_data=f"decision_show_become_admin_decline_{user_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_list)
