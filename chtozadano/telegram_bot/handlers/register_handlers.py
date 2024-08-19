import asyncio
import os
import random

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from constants import DOCKER_URL, DOMAIN_URL
from handlers.menu_handlers import command_menu_handler
from keyboards import kb_menu, kb_start
import requests
from states import Register
from utils import check_for_admin, delete_become_admin

rp_register_router = Router()


@rp_register_router.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/is_user_in_system/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    if response.text.lower() == "true":
        await message.answer(
            "Вы уже выбрали класс, для смены класса введите /reset",
        )
        await command_menu_handler(message)
    else:
        await state.set_state(Register.choose_class)
        await message.answer(
            "Привет!\nЧтобы начать работу, выбери класс,"
            " в котором ты учишься в этом году",
            reply_markup=kb_start.choose_gr_let_in_kb(),
        )


@rp_register_router.message(Command("reset"))
async def command_reset_handler(message: Message, state: FSMContext) -> None:
    if await check_for_admin(message.from_user.id) == "admin":
        await message.answer(
            "Ты назначен администратором в своем классе,"
            " поэтому не можешь поменять класс\n\n"
            "Если тебе необходимо посмотреть домашку"
            " для другого класса, то воспользуйся сайтом\n\n"
            "Если ты больше не хочешь быть администратором -"
            " напиши одному из главных администраторов:\n"
            "· @alex010407\n· @tabara_bulkala",
            reply_markup=kb_menu.menu_rp_kb(),
        )
    else:
        await delete_become_admin(message.from_user.id)
        await state.set_state(Register.choose_class)
        await message.answer(
            "Выбери класс, в котором ты учишься в этом году",
            reply_markup=kb_start.choose_gr_let_in_kb(),
        )


@rp_register_router.callback_query(
    Register.choose_class,
    F.data.startswith("ch_gr_let_"),
)
async def choose_group_handler(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(f"Вы выбрали {call.data.split('_')[-1]}")
    await state.update_data(choose_class=call.data.split("_")[-1])
    await state.set_state(Register.choose_group)
    await call.message.answer(
        "Теперь выберите группу в которой вы учитесь",
        reply_markup=kb_start.choose_group_in_kb(),
    )


@rp_register_router.callback_query(
    Register.choose_group,
    F.data.startswith("ch_group_"),
)
async def start_redirect_to_menu_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.update_data(choose_group=call.data.split("_")[-1])
    user_data = await state.get_data()
    grade = user_data["choose_class"][:-1]
    letter = user_data["choose_class"][-1]
    group = user_data["choose_group"]

    await call.message.answer(
        f"Вы в {html.italic(grade)}{html.italic(letter)}"
        f" классе, группа {html.italic(group)}",
    )
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/create_user/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": call.from_user.id,
            "grade": grade,
            "letter": letter,
            "group": group,
            "name": call.from_user.username,
        },
    )
    await state.clear()
    await call.message.answer(
        "На этом всё. Теперь я всегда готов ответить на"
        " твои вопросы по домашнему заданию. Чтобы"
        " узнать домашнее задание, отправь вопрос в"
        " произвольной форме, обязательно упомянув"
        " название предмета.\nА если вдруг у тебя не"
        " будет возможности спросить меня, все домашние"
        " задания доступны через сайт https://hw116.ru"
        " И не забывай - описание всех доступных функций"
        " всегда доступно через команду /help",
    )
    await command_menu_handler(call.message)


@rp_register_router.callback_query(
    F.data == "back_to_start",
    Register.choose_group,
)
async def redirect_to_start_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(Register.start)
    await command_start_handler(call.message, state)


@rp_register_router.message(Command("code"))
async def site_register_handler(message: Message) -> None:
    confirmation_code = random.randint(111111, 999999)
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/code_confirmation/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
            "confirmation_code": confirmation_code,
            "name": message.from_user.first_name,
        },
    )
    if response.status_code == 200:
        await message.answer(
            f"Ваш код для входа: {html.code(confirmation_code)}",
            reply_markup=kb_start.open_site_in_kb(DOMAIN_URL),
        )
    else:
        await message.answer("Ошибка сервера")
