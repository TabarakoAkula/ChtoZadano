import asyncio
import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from constants import DOCKER_URL, WEEK_DAYS
from filters import ScheduleStateFilter
from keyboards import kb_schedule
import requests
from states import Schedule

rp_schedule_router = Router()


@rp_schedule_router.message(F.text == "Расписание🗓")
async def schedule_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Schedule.start)
    await message.answer(
        "Выбери какое расписание ты хочешь посмотреть",
        reply_markup=kb_schedule.schedule_rp_kb(),
    )


@rp_schedule_router.message(F.text == "На неделю", ScheduleStateFilter)
async def schedule_week_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Schedule.week_schedule)
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_week_schedule/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    await message.answer(
        "Расписание на неделю для твоей группы:",
        reply_markup=kb_schedule.schedule_rp_kb(),
    )
    schedule = response.json()
    weekday_now = 0
    result_message = ""
    for i in schedule:
        try:
            if i["weekday"] == weekday_now:
                result_message += f"{i['lesson']}. {i['subject']}\n"
            else:
                result_message += f"\n{WEEK_DAYS[i['weekday']]}:\n"
                result_message += f"{i['lesson']}. {i['subject']}\n"
                weekday_now = i["weekday"]
        except (KeyError, TypeError):
            await message.answer(
                "Для взаимодействия с ботом необходимо"
                " в нем зарегистрироваться."
                " Введи команду /start",
            )
            return
    await message.answer(
        result_message,
        reply_markup=kb_schedule.schedule_rp_kb(),
    )


@rp_schedule_router.message(F.text == "На завтра", ScheduleStateFilter)
async def schedule_tomorrow_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Schedule.tomorrow_schedule)
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_tomorrow_schedule/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    await message.answer(
        "Расписание на завтра для твоей группы:",
        reply_markup=kb_schedule.schedule_rp_kb(),
    )
    schedule = response.json()
    try:
        result_message = WEEK_DAYS[schedule[0]["weekday"]] + ":"
    except (KeyError, TypeError):
        await message.answer(
            "Для взаимодействия с ботом необходимо в нем зарегистрироваться."
            " Введи команду /start",
        )
        return
    for i in schedule:
        result_message += f"\n{i['lesson']}. {i['subject']}"
    await message.answer(
        result_message,
        reply_markup=kb_schedule.schedule_rp_kb(),
    )


@rp_schedule_router.message(Command("get_week_schedule"))
async def command_week_schedule_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await schedule_week_handler(message, state)


@rp_schedule_router.message(Command("get_tomorrow_schedule"))
async def command_tomorrow_schedule_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await schedule_tomorrow_handler(message, state)
