import asyncio
import os

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from constants import DOCKER_URL
from filters import (
    HomeworkStateFilter,
    StopAddHomeworkStateFilter,
)
from handlers.homework_handlers import add_homework_handler
from handlers.menu_handlers import command_menu_handler
from keyboards.homework import (
    homework_menu,
    homework_subject,
)
import requests
from states import Homework
from utils import (
    check_for_admin,
    generate_homework,
    get_homework_from_date,
    get_user_subjects,
)

rp_homework_menu_router = Router()


@rp_homework_menu_router.message(Command("new"))
async def command_add_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await add_homework_handler(message, state)


@rp_homework_menu_router.message(Command("stop"), StopAddHomeworkStateFilter)
async def command_stop_add_homework_handler(
    message: Message,
) -> None:
    await command_menu_handler(message)


@rp_homework_menu_router.message(F.text == "Домашка📝")
async def homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Homework.start)
    if await check_for_admin(message.chat.id) in ["admin", "superuser"]:
        keyboard = homework_menu.homework_main_admin_rp_kb()
    else:
        keyboard = homework_menu.homework_main_user_rp_kb()
    await message.answer(
        text="Список доступных опций:",
        reply_markup=keyboard,
    )


@rp_homework_menu_router.message(
    F.text == "Домашка на завтра⏰",
    HomeworkStateFilter,
)
async def tomorrow_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_tomorrow_homework/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    response_data = response.json()
    if response_data:
        for record in response_data:
            homework = response_data[record]
            await generate_homework(homework, record, message)
    else:
        await message.answer("На завтра ничего не задано")
    await homework_handler(message, state)


@rp_homework_menu_router.message(Command("tomorrow"))
async def command_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await tomorrow_homework_handler(message, state)


@rp_homework_menu_router.message(
    F.text == "Выбрать предмет📚",
    HomeworkStateFilter,
)
async def get_subject_hw_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Homework.subject)
    subjects = await get_user_subjects(message.chat.id)
    subjects.append("информация")
    await message.answer(
        text="Выбери предмет, по которому хочешь увидеть последнюю домашку",
        reply_markup=homework_subject.homework_subject_in_kb(
            subjects=subjects,
            add=False,
        ),
    )


@rp_homework_menu_router.callback_query(
    F.data.startswith("homework_subject_"),
    HomeworkStateFilter,
)
async def callback_homework_subject(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(Homework.subject)
    subject = call.data.split("_")[-1]
    if subject != "Информация":
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/get_homework_for_subject/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": call.from_user.id,
                "subject": subject.lower(),
            },
        )
        response_data = response.json()
        await generate_homework(response_data, 0, call.message)
    else:
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/get_mailing/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": call.from_user.id,
            },
        )
        response_data = response.json()
        response_data["subject"] = "Информация"
        await generate_homework(response_data, 0, call.message)


@rp_homework_menu_router.message(Command("subject"))
async def command_redirect_homework_subject(
    message: Message,
    state: FSMContext,
) -> None:
    await get_subject_hw_handler(message, state)


@rp_homework_menu_router.message(
    F.text == "Найти домашку🔎",
    HomeworkStateFilter,
)
async def search_homework_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(Homework.find)
    await message.answer(
        text="Ты можешь найти домашнее задание, если оно было"
        " опубликовано меньше чем 2 недели назад."
        "\n\nЧтобы посмотреть всю домашку за определенную дату,"
        " введи ее формате год.месяц.день",
        reply_markup=homework_menu.return_to_homework_rp_kb(),
    )


@rp_homework_menu_router.message(F.text == "Назад", HomeworkStateFilter)
async def return_to_homework(
    message: Message,
    state: FSMContext,
) -> None:
    await homework_handler(message, state)


@rp_homework_menu_router.message(Homework.find)
async def search_hw_function_handler(
    message: Message,
):
    if len(message.text.split(".")) != 3:
        return
    homeworks = await get_homework_from_date(message.chat.id, message.text)
    if not homeworks:
        await message.answer(
            f"Сохраненных домашних заданий на"
            f" {html.italic(message.text)} нет.\n\n"
            f"Проверь корректность ввода даты",
        )
        return
    await message.answer(
        f"Домашние задания, опубликованные {html.italic(message.text)}:",
    )
    counter = 1
    for homework in homeworks:
        await generate_homework(homework, counter, message)
        counter += 1


@rp_homework_menu_router.message(Command("date"))
async def command_search_hw_handler(
    message: Message,
    state: FSMContext,
):
    await search_homework_handler(message, state)
