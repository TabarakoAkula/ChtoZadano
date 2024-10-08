import asyncio
import os
import random

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from constants import DOCKER_URL, DOMAIN_URL
from filters import ReturnToStartRegistrationStateFilter
from handlers.menu_handlers import command_menu_handler
from keyboards import kb_menu, kb_start
import requests
from states import Register
from utils import (
    check_for_admin,
    create_user,
    delete_become_admin,
    get_all_classes,
)

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
            "Ты уже выбрал класс, для смены класса введи /reset",
        )
        await command_menu_handler(message)
    else:
        await state.set_state(Register.choose_class)
        await message.answer(
            "Привет!\nЧтобы начать работу, выбери класс,"
            " в котором ты учишься в этом году",
            reply_markup=kb_start.choose_gr_let_in_kb(await get_all_classes()),
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
            reply_markup=kb_start.choose_gr_let_in_kb(await get_all_classes()),
        )


@rp_register_router.callback_query(
    Register.choose_class,
    F.data.startswith("ch_gr_let_"),
)
async def choose_group_handler(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(f"Ты выбрал {call.data.split('_')[-1]}")
    grade_letter = call.data.split("_")[-1]
    await state.update_data(choose_class=grade_letter)
    letter = grade_letter[-1]
    grade = int(grade_letter[:-1])
    teachers = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_user_eng_teachers/",
        json={
            "api_key": os.getenv("API_KEY"),
            "grade": grade,
            "letter": letter,
        },
    )
    teachers = teachers.json()["teachers"]
    await state.set_state(Register.choose_group)
    await call.message.answer(
        "Теперь выбери у какого учителя английского ты учишься",
        reply_markup=kb_start.choose_group_in_kb(teachers[0], teachers[1]),
    )


@rp_register_router.callback_query(
    Register.choose_group,
    F.data.startswith("ch_group_"),
)
async def start_redirect_to_menu_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    user_data = await state.get_data()
    grade = user_data["choose_class"][:-1]
    letter = user_data["choose_class"][-1]
    group = str(
        call.data.split("_")[-2] + " " + call.data.split("_")[-1],
    ).replace(" ", "_")
    await state.update_data(
        {
            "grade": grade,
            "letter": letter,
            "group": group,
        },
    )
    await state.set_state(Register.become_admin)
    await call.message.answer(
        f"Ты в {html.italic(grade)}{html.italic(letter)}"
        f" классе, группа {html.italic(group.replace('_', ' '))}",
    )
    await call.message.answer(
        "И последний вопрос: ты хочешь стать администратором в своем классе?",
        reply_markup=kb_start.start_become_admin_in_kb(),
    )


@rp_register_router.callback_query(
    Register.become_admin,
    F.data == "start_become_admin_no",
)
async def registration_go_menu_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await create_user(call, state)
    await command_menu_handler(call.message)


@rp_register_router.callback_query(
    F.data == "back_to_start",
    ReturnToStartRegistrationStateFilter,
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
            f"Твой код для входа: {html.code(confirmation_code)}",
            reply_markup=kb_start.open_site_in_kb(DOMAIN_URL),
        )
    else:
        await message.answer("Ошибка сервера")
