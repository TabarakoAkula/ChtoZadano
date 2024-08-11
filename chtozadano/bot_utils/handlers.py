import asyncio
import json
import os
import random

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot_utils import keyboards
from bot_utils.filters import ScheduleStateFilter
from bot_utils.states import Register, Schedule
import dotenv
import requests

dotenv.load_dotenv()

DOMAIN_URL = os.getenv("DOMAIN_URL")
DOCKER_URL = os.getenv("DOCKER_URL")

MENU_MESSAGES = [
    "Какой сегодня чудный день🔮",
    f"Мы все учились понемногу чему-нибудь и как-нибудь.\n"
    f"- {html.italic('Александр Сергеевич Пушкин')}",
    f"Учение — только свет, по народной пословице, — оно также и свобода."
    f" Ничто так не освобождает человека, как знание.\n"
    f"- {html.italic('Иван Сергеевич Тургенев')}",
    f"Чему бы ты ни учился, ты учишься для себя.\n"
    f"- {html.italic('Петроний Арбитр Гай')}",
    f"В учении нельзя останавливаться.\n- {html.italic('Сюнь-цзы')}",
    f"Самостоятельность головы учащегося — единственное прочное основание"
    f" всякого плодотворного учения.\n"
    f"- {html.italic('Константин Дмитриевич Ушинский')}",
    f"Кто ни о чем не спрашивает, тот ничему не научится.\n"
    f"- {html.italic('Томас Фуллер')}",
    f"Надо много учиться, чтобы знать хоть немного.\n"
    f"- {html.italic('Шарль Луи Монтескье')}",
    f"Тот, кто не желает учиться, — никогда не станет настоящим человеком.\n"
    f"- {html.italic('Хосе Хулиан Марти')}",
    f"Ученье свет, а неученье — тьма. Дело мастера боится.\n"
    f"- {html.italic('Александр Васильевич Суворов')}",
    f"Ни искусство, ни мудрость не могут быть достигнуты,"
    f" если им не учиться.\n"
    f"- {html.italic('Демокрит')}",
    f"Надо много учиться, чтобы осознать, что знаешь мало.\n"
    f"- {html.italic('Мишель де Монтень')}",
]

WEEK_DAYS = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
}

rp = Router()


@rp.message(Command("help"))
async def command_help_handler(message: Message):
    await message.answer(
        "/start - инициализировать бота\n"
        "/reset - сменить класс\n"
        "/menu - меню\n"
        "/code - код верификации\n"
        "/get_week_schedule - расписание на неделю\n"
        "/get_tomorrow_schedule - расписание на завтра\n",
    )


@rp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext):
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
            reply_markup=keyboards.choose_gr_let_in_kb(),
        )


@rp.message(Command("reset"))
async def command_reset_handler(message: Message, state: FSMContext):
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/is_user_admin/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    response_data = json.loads(response.json())
    if response_data["is_admin"] and not response_data["is_superuser"]:
        await message.answer(
            "Ты назначен администратором в своем классе,"
            " поэтому не можешь поменять класс\n\n"
            "Если тебе необходимо посмотреть домашку"
            " для другого класса, то воспользуйся сайтом\n\n"
            "Если ты больше не хочешь быть администратором -"
            " напиши одному из главных администраторов:\n"
            "· @alex010407\n· @tabara_bulkala",
        )
    else:
        await state.set_state(Register.choose_class)
        await message.answer(
            "Выбери класс, в котором ты учишься в этом году",
            reply_markup=keyboards.choose_gr_let_in_kb(),
        )


@rp.callback_query(Register.choose_class, F.data.startswith("ch_gr_let_"))
async def choose_group_handler(call: CallbackQuery, state: FSMContext):
    await call.answer(f"Вы выбрали {call.data.split('_')[-1]}")
    await state.update_data(choose_class=call.data.split("_")[-1])
    await state.set_state(Register.choose_group)
    await call.message.answer(
        "Теперь выберите группу в которой вы учитесь",
        reply_markup=keyboards.choose_group_in_kb(),
    )


@rp.callback_query(Register.choose_group, F.data.startswith("ch_group_"))
async def start_redirect_to_menu_handler(
    call: CallbackQuery,
    state: FSMContext,
):
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


@rp.message(Command("menu"))
async def command_menu_handler(message: Message):
    await message.answer(
        text=random.choice(MENU_MESSAGES),
        reply_markup=keyboards.menu_rp_kb(),
    )


@rp.callback_query(F.data == "back_to_start", Register.choose_group)
async def redirect_to_start_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(Register.start)
    await command_start_handler(call.message, state)


@rp.message(Command("code"))
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
            reply_markup=keyboards.open_site_in_kb(DOMAIN_URL),
        )
    else:
        await message.answer("Ошибка сервера")


@rp.message(F.text == "Расписание🗓")
async def schedule_handler(message: Message, state: FSMContext):
    await state.set_state(Schedule.start)
    await message.answer(
        "Выбери какое расписание ты хочешь посмотреть",
        reply_markup=keyboards.schedule_rp_kb(),
    )


@rp.message(F.text == "На неделю", ScheduleStateFilter)
async def schedule_week_handler(message: Message, state: FSMContext):
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
        reply_markup=keyboards.schedule_rp_kb(),
    )
    schedule = response.json()
    weekday_now = 0
    result_message = ""
    for i in schedule:
        if i["weekday"] == weekday_now:
            result_message += f"{i['lesson']}. {i['subject']}\n"
        else:
            result_message += f"\n{WEEK_DAYS[i['weekday']]}:\n"
            result_message += f"{i['lesson']}. {i['subject']}\n"
            weekday_now = i["weekday"]
    await message.answer(
        result_message,
        reply_markup=keyboards.schedule_rp_kb(),
    )


@rp.message(F.text == "На завтра", ScheduleStateFilter)
async def schedule_tomorrow_handler(message: Message, state: FSMContext):
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
        reply_markup=keyboards.schedule_rp_kb(),
    )
    schedule = response.json()
    result_message = WEEK_DAYS[schedule[0]["weekday"]] + ":"
    for i in schedule:
        result_message += f"\n{i['lesson']}. {i['subject']}"
    await message.answer(
        result_message,
        reply_markup=keyboards.schedule_rp_kb(),
    )


@rp.message(F.text == "Вернуться", ScheduleStateFilter)
async def schedule_back_handler(message: Message, state: FSMContext):
    await state.clear()
    await command_menu_handler(message)


@rp.message(Command("get_week_schedule"))
async def command_week_schedule_handler(
    message: Message,
    state: FSMContext,
):
    await schedule_week_handler(message, state)


@rp.message(Command("get_tomorrow_schedule"))
async def command_tomorrow_schedule_handler(
    message: Message,
    state: FSMContext,
):
    await schedule_tomorrow_handler(message, state)
