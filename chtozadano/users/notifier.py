import os

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import dotenv

dotenv.load_dotenv()


async def become_admin_notify(
    number_of_requests: int,
    users_ids: list[int],
) -> None:
    async with AiohttpSession() as bot_session:
        notify_bot = Bot(token=os.getenv("BOT_TOKEN"), session=bot_session)
        for user_id in users_ids:
            await notify_bot.send_message(
                chat_id=user_id,
                text=(
                    f"👮Новая заявка на становление администратором"
                    f"\nВсего заявок: {number_of_requests}"
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Посмотреть заявки",
                                callback_data="become_admin_requests",
                            ),
                        ],
                    ],
                ),
            )
        return


async def custom_notification(
    users_ids: list,
    message_text: str,
    notification: bool,
) -> None:
    async with AiohttpSession() as bot_session:
        notify_bot = Bot(token=os.getenv("BOT_TOKEN"), session=bot_session)
        for user_id in users_ids:
            await notify_bot.send_message(
                chat_id=user_id,
                text=message_text,
                disable_notification=not notification,
            )
        return
