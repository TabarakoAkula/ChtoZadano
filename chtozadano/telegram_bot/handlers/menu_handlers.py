import asyncio
import os
import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from constants import DOCKER_URL, MENU_MESSAGES
from keyboards import kb_menu
import requests

rp_menu_router = Router()


@rp_menu_router.message(Command("menu"))
async def command_menu_handler(
    message: Message,
    show_quotes: bool = True,
) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_quotes_status/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    if response.json()["quotes_status"] and show_quotes:
        await message.answer(
            text=random.choice(MENU_MESSAGES),
            reply_markup=kb_menu.menu_rp_kb(),
        )
    elif show_quotes:
        await message.answer(
            text="Ты находишься в основном меню",
            reply_markup=kb_menu.menu_rp_kb(),
        )


@rp_menu_router.message(F.text == "Вернуться")
async def schedule_back_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await command_menu_handler(message)


@rp_menu_router.callback_query(F.data == "back_to_menu")
async def inline_back_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("Редактирование домашнего задания отменено❌")
    await command_menu_handler(call.message)
