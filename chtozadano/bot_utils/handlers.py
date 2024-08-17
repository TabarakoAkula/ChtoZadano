import asyncio
import datetime
import os
import random

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from bot_utils import keyboards
from bot_utils.bot import bot
from bot_utils.filters import (
    AccountStateFilter,
    AddHomeworkStateFilter,
    EditHomeworkStateFilter,
    HomeworkStateFilter,
    PublishHomeworkStateFilter,
    ScheduleStateFilter,
)
from bot_utils.message_texts import MENU_MESSAGES, SUBJECTS, WEEK_DAYS
from bot_utils.states import (
    Account,
    AddHomework,
    ChangeContacts,
    EditHomework,
    Homework,
    Register,
    Schedule,
)
from bot_utils.utils import (
    bot_save_files,
    check_for_admin,
    delete_become_admin,
    delete_homework,
    edit_hw_description,
    generate_homework,
    get_homework_from_id,
    get_user_subjects,
    publish_homework,
)
import dotenv
import requests

dotenv.load_dotenv()

DOMAIN_URL = os.getenv("DOMAIN_URL")
DOCKER_URL = os.getenv("DOCKER_URL")

rp = Router()


@rp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        "/start - инициализировать бота\n"
        "/reset - сменить класс\n"
        "/menu - меню\n"
        "/code - код верификации\n"
        "/get_week_schedule - расписание на неделю\n"
        "/get_tomorrow_schedule - расписание на завтра\n"
        "/change_contacts - изменить имя или фамилию\n"
        "/become_admin - стать администратором\n"
        "/settings - настройки\n"
        "/tomorrow - посмотреть дз на завтра\n"
        "/subject - посмотреть дз по конкретному предмету\n"
        "/new - добавить домашнее задание\n"
        "/publish - опубликовать домашнее задание\n"
        "/stop - прекратить добавление домашнего задания\n",
    )


# /show_become_admin - просмотр заявок на администратора
# /add_mailing - добавить информацию


@rp.message(Command("start"))
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
            reply_markup=keyboards.choose_gr_let_in_kb(),
        )


@rp.message(Command("reset"))
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
            reply_markup=keyboards.menu_rp_kb(),
        )
    else:
        await delete_become_admin(message.from_user.id)
        await state.set_state(Register.choose_class)
        await message.answer(
            "Выбери класс, в котором ты учишься в этом году",
            reply_markup=keyboards.choose_gr_let_in_kb(),
        )


@rp.callback_query(Register.choose_class, F.data.startswith("ch_gr_let_"))
async def choose_group_handler(call: CallbackQuery, state: FSMContext) -> None:
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


@rp.message(Command("menu"))
async def command_menu_handler(message: Message) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_quotes_status/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    if response.json()["quotes_status"]:
        await message.answer(
            text=random.choice(MENU_MESSAGES),
            reply_markup=keyboards.menu_rp_kb(),
        )
    else:
        await message.answer(
            text="Ты находишься в основном меню",
            reply_markup=keyboards.menu_rp_kb(),
        )


@rp.callback_query(F.data == "back_to_start", Register.choose_group)
async def redirect_to_start_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
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
async def schedule_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Schedule.start)
    await message.answer(
        "Выбери какое расписание ты хочешь посмотреть",
        reply_markup=keyboards.schedule_rp_kb(),
    )


@rp.message(F.text == "На неделю", ScheduleStateFilter)
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


@rp.message(F.text == "Вернуться")
async def schedule_back_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await command_menu_handler(message)


@rp.callback_query(F.data == "back_to_menu")
async def inline_back_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("Редактирование домашнего задания отменено❌")
    await command_menu_handler(call.message)


@rp.message(Command("get_week_schedule"))
async def command_week_schedule_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await schedule_week_handler(message, state)


@rp.message(Command("get_tomorrow_schedule"))
async def command_tomorrow_schedule_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await schedule_tomorrow_handler(message, state)


@rp.message(F.text == "Аккаунт👤")
async def account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Account.start)
    if await check_for_admin(message.from_user.id) == "admin":
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=keyboards.account_admin_page_rp_kb(),
        )
    else:
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=keyboards.account_user_page_rp_kb(),
        )


@rp.message(F.text == "Имя и Фамилия✏️", AccountStateFilter)
async def change_contacts_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    if await check_for_admin(message.chat.id) == "admin":
        await message.answer(
            "Ты являешься администратором, поэтому"
            " не можешь менять свои данные без разрешения"
            " главных администраторов",
        )
        await account_handler(message, state)
        return
    await state.set_state(Account.change_contacts)
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_contacts/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    response = response.json()
    first_name = response["first_name"]
    last_name = response["last_name"]
    answer_message = (
        f"Сейчас твои данные выглядят так:\nИмя: {html.bold(first_name)}\n"
        f"Фамилия: {html.bold(last_name)}\n\nЭти данные будут отображаться"
        f" при добавлении домашнего задания, а также при отправке"
        f" заявки на становление администратором"
    )
    await message.answer(
        text=answer_message,
        reply_markup=keyboards.change_contacts_rp_kb(),
    )


@rp.message(F.text == "Назад", AccountStateFilter)
async def redirect_to_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Account.start)
    if await check_for_admin(message.from_user.id) == "admin":
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=keyboards.account_admin_page_rp_kb(),
        )
    else:
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=keyboards.account_user_page_rp_kb(),
        )


@rp.message(F.text == "Изменить данные📝", AccountStateFilter)
async def first_name_change_contacts_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(ChangeContacts.first_name)
    await message.answer(
        "Введи свое имя:",
    )


@rp.message(ChangeContacts.first_name)
async def last_name_change_contacts_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(first_name=message.text)
    await state.set_state(ChangeContacts.last_name)
    await message.answer(
        "Введи свою фамилию:",
    )


@rp.message(ChangeContacts.last_name)
async def redirect_from_change_contacts_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    data["first_name"] = data["first_name"][:15]
    data["last_name"] = data["last_name"][:15]
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/change_contacts/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
            "first_name": data["first_name"],
            "last_name": data["last_name"],
        },
    )
    await state.clear()
    await change_contacts_account_handler(message, state)


@rp.message(Command("change_contacts"))
async def redirect_change_contacts(
    message: Message,
    state: FSMContext,
) -> None:
    await change_contacts_account_handler(message, state)


@rp.message(F.text == "Сменить класс🏫", AccountStateFilter)
async def change_class_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await command_reset_handler(message, state)


@rp.message(F.text == "Стать администратором👨‍💼", AccountStateFilter)
async def become_admin_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_contacts/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.from_user.id,
        },
    )
    if await check_for_admin(message.from_user.id) == "admin":
        await state.set_state(Account.start)
        await message.answer(
            "Ты уже являешься администратором😉",
            reply_markup=keyboards.account_admin_page_rp_kb(),
        )
    else:
        response = response.json()
        first_name = response["first_name"]
        last_name = response["last_name"]
        await message.answer(
            text=f"Став администратором, у тебя появится возможность добавлять"
            f" и редактировать домашние задания.\n\nПеред отправкой заявки"
            f" обязательно проверь свои данные:\n"
            f"Имя: {html.bold(first_name)}\n"
            f"Фамилия: {html.bold(last_name)}\n\n"
            f"Данные можно изменить в меню {html.bold('Имя и фамилия✏️')},"
            f" или введя команду /change_contacts\n"
            f"Для отправки заявки нажми кнопку ниже👇",
            reply_markup=keyboards.become_admin_rp_kb(),
        )


@rp.message(Command("become_admin"))
async def command_become_admin_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await become_admin_account_handler(message, state)


@rp.message(F.text == "Отправить заявку📁")
async def send_become_admin_handler(
    message: Message,
    state: FSMContext,
) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/become_admin/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    response_data = response.json()
    try:
        answer = response_data["error"]
    except KeyError:
        answer = response_data["success"]
    if answer == "Wait pls":
        await message.answer(
            text="Заявка уже была отправлена, пожалуйста, подождите⏰",
        )
    elif answer == "Successful":
        await message.answer(
            "✅Заявка успешно отправлена, если она не будет рассмотрена за 48"
            " часов - свяжись с главными администраторами:\n"
            "· @alex010407\n· @tabara_bulkala",
        )
    elif answer == "You are already admin":
        await message.answer(
            "Ты уже являешься администратором",
        )
    await state.set_state(Account.start)


@rp.message(Command("show_become_admin"))
async def command_show_become_admin_handler(
    message: Message,
) -> None:
    if await check_for_admin(message.chat.id) == "superuser":
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/show_become_admin/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": message.chat.id,
            },
        )
        data = response.json()
        if not data:
            await message.answer("Заявок пока что нет :/")
            return
        for request in data:
            created_at = datetime.datetime.strptime(
                request["created_at"],
                "%Y-%m-%dT%H:%M:%S.%f",
            ).date()
            user_id = request["telegram_id"]
            await message.answer(
                f"Заявка №{request['id']}\n\nКласс: {request['grade']}"
                f"{request['letter']}\nГруппа: {request['group']}\n"
                f"Имя: {request['first_name']}\n"
                f"Фамилия: {request['last_name']}\n"
                f"Дата: {created_at}\n"
                f"tg://openmessage?user_id={request['telegram_id']}\n",
                reply_markup=keyboards.show_become_admin_in_kb(user_id),
            )


@rp.callback_query(F.data.startswith("decision_show_become_admin_"))
async def decision_show_become_admin(
    call: CallbackQuery,
) -> None:
    await call.message.delete()
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/become_admin_accept_decline/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": call.from_user.id,
            "candidate_id": call.data.split("_")[-1],
            "decision": call.data.split("_")[-2],
        },
    )


@rp.message(F.text == "Настройки🛠️")
async def settings_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Account.settings)
    chat_mode = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_chat_mode/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    quotes_status = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_quotes_status/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    chat_mode = chat_mode.json()["chat_mode"]
    if chat_mode:
        chat_mode = "Включен"
    else:
        chat_mode = "Выключен"
    quotes_status = quotes_status.json()["quotes_status"]
    if quotes_status:
        quotes_status = "Включен"
    else:
        quotes_status = "Выключен"
    await message.answer(
        text="Здесь ты сможешь настроить:\n· Режим чата - если включено, "
        "то при добавлении новой домашки - ты увидишь ее\n"
        "· Режим цитат - если включено, то при открытии меню (/menu)"
        " ты увидишь случайную цитату",
    )
    await message.answer(
        text=f"Текущие настройки:\n"
        f"· Режим чата: {html.bold(chat_mode)}\n"
        f"· Режим цитат: {html.bold(quotes_status)}",
        reply_markup=keyboards.settings_rp_kb(),
    )


@rp.message(F.text == "Сменить режим чата💬", AccountStateFilter)
async def chat_mode_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/change_chat_mode/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    await settings_handler(message, state)


@rp.message(F.text == "Сменить режим цитат📓", AccountStateFilter)
async def quotes_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/change_quotes/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": message.chat.id,
        },
    )
    await settings_handler(message, state)


@rp.message(Command("settings"))
async def command_settings_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await settings_handler(message, state)


@rp.message(F.text == "Домашка📝")
async def homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Homework.start)
    if await check_for_admin(message.chat.id) in ["admin", "superuser"]:
        keyboard = keyboards.homework_main_admin_rp_kb()
    else:
        keyboard = keyboards.homework_main_user_rp_kb()
    await message.answer(
        text="Список доступных опций:",
        reply_markup=keyboard,
    )


@rp.message(F.text == "Домашка на завтра⏰", HomeworkStateFilter)
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


@rp.message(Command("tomorrow"))
async def command_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await tomorrow_homework_handler(message, state)


@rp.message(F.text == "Выбрать предмет📚", HomeworkStateFilter)
async def get_subject_hw_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Homework.subject)
    subjects = await get_user_subjects(message.chat.id)
    subjects.append("информация")
    await message.answer(
        text="Выбери предмет, по которому хочешь увидеть последнюю домашку",
        reply_markup=keyboards.homework_subject_in_kb(
            subjects=subjects,
            add=False,
        ),
    )


@rp.callback_query(F.data.startswith("homework_subject_"), HomeworkStateFilter)
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


@rp.message(Command("subject"))
async def command_redirect_homework_subject(
    message: Message,
    state: FSMContext,
) -> None:
    await get_subject_hw_handler(message, state)


@rp.message(F.text.lower().in_(SUBJECTS))
async def enter_subject_handler(
    message: Message,
) -> None:
    subject = SUBJECTS[message.text.lower()]
    if subject != "info":
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/get_homework_for_subject/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": message.chat.id,
                "subject": subject,
                "use_abbreviation": True,
            },
        )
        response_data = response.json()
        if response.status_code == 406:
            await message.answer("В твоем классе нет такого предмета")
            return
    else:
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/get_mailing/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": message.chat.id,
            },
        )
        response_data = response.json()
        response_data["subject"] = "Информация"
    await generate_homework(homework=response_data, record=0, message=message)


@rp.message(F.text == "Добавить📋", HomeworkStateFilter)
async def add_homework_handler(
    message: Message,
    state: FSMContext,
    mailing: bool = False,
) -> None:
    await state.set_state(AddHomework.choose_subject)
    subjects = await get_user_subjects(message.chat.id)
    subjects.append("информация")
    keyboard = keyboards.homework_subject_in_kb(
        subjects=subjects,
        add=True,
    )
    text = "Выбери предмет, по которому хочешь добавить домашку"
    if mailing:
        keyboard = keyboards.get_mailings()
        text = "Выбери уровень рассылки"
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )


@rp.callback_query(
    F.data.startswith("add_hw_subject_"),
    AddHomeworkStateFilter,
)
async def choose_subject_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    subject = call.data.split("_")[-1]
    await state.update_data(choose_subject=subject)
    await state.update_data(images=[])
    await state.update_data(files=[])
    await state.update_data(message_id=[])
    await state.set_state(AddHomework.add_descriptions_images)
    await call.answer(f"Выбранный предмет: {subject}")
    await call.message.answer(
        text="Отлично, теперь отправь домашку\n(Ты можешь отправить"
        " изображения и описание, файлы можно будет отправить позже)",
    )


@rp.callback_query(F.data == "add_homework_files", AddHomeworkStateFilter)
async def add_homework_files_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await call.message.delete_reply_markup()
    await call.message.answer(
        text="Отправь файлы, которые хочешь прикрепить к домашке"
        " (размер файла не должен превышать 20Мб)\n"
        "Для корректного добавления - дождись уведомления о том,"
        " что файл добавлен",
        reply_markup=keyboards.add_homework_maximum_in_kb(),
    )
    await state.set_state(AddHomework.add_files)


@rp.message(
    AddHomework.add_files,
    F.content_type.in_([ContentType.DOCUMENT, ContentType.AUDIO]),
)
async def add_files_handler(
    message: Message,
    state: FSMContext,
) -> None:
    state_data = await state.get_data()
    subject = state_data["choose_subject"]
    if message.document:
        for idx, document in enumerate(message.document):
            if document[0] == "file_id":
                await message.answer(
                    f"Файл {html.italic(message.document.file_name)}"
                    f" был отправлен на обработку",
                )
                await bot_save_files(
                    bot,
                    "files",
                    "files",
                    document,
                    message,
                    subject,
                    state,
                    message.document.file_name,
                )
    if message.audio:
        for idx, music in enumerate(message.audio):
            if music[0] == "file_id":
                await message.answer(
                    f"Файл {html.italic(message.audio.file_name)}"
                    f" был отправлен на обработку",
                )
                await bot_save_files(
                    bot,
                    "music",
                    "files",
                    music,
                    message,
                    subject,
                    state,
                    message.audio.file_name,
                )


@rp.callback_query(F.data == "publish_hw")
async def publish_hw_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    state_data = await state.get_data()
    status_code, homework_id = await publish_homework(
        data=state_data,
        telegram_id=call.message.chat.id,
    )
    if status_code == 200:
        if homework_id != -1:
            await call.message.answer(
                text="Домашнее задание успешно опубликовано",
                reply_markup=keyboards.to_edit_homework_in_kb(homework_id),
            )
        else:
            await call.message.answer(
                text="Информация успешно опубликована",
                reply_markup=keyboards.delete_mailing_in_kb(),
            )
    await state.clear()
    await command_menu_handler(call.message)


@rp.message(Command("publish"), PublishHomeworkStateFilter)
async def command_publish_hw_handler(
    message: Message,
    state: FSMContext,
) -> None:
    state_data = await state.get_data()
    status_code, homework_id = await publish_homework(
        data=state_data,
        telegram_id=message.chat.id,
    )
    if status_code == 200:
        if homework_id != -1:
            await message.answer(
                text="Домашнее задание успешно опубликовано",
                reply_markup=keyboards.to_edit_homework_in_kb(homework_id),
            )
        else:
            await message.answer(
                text="Информация успешно опубликована",
                reply_markup=keyboards.delete_mailing_in_kb(),
            )
    await state.clear()
    await command_menu_handler(message)


@rp.message(
    AddHomework.add_descriptions_images,
    F.content_type.in_([ContentType.TEXT, ContentType.PHOTO]),
)
async def add_description_images_handler(
    message: Message,
    state: FSMContext,
) -> None:
    text = message.caption or message.text
    state_data = await state.get_data()
    subject = state_data["choose_subject"]
    if text:
        await state.update_data(text=text)
    data = await state.get_data()
    state_message_id = data["message_id"]
    text = data["text"]
    state_message_id.append(message.message_id)
    await state.update_data(message_id=state_message_id)
    if message.photo and text:
        if len(state_message_id) == 1:
            await message.answer(
                text="Фотографии и текст успешно загружены",
                reply_markup=keyboards.add_homework_in_kb(),
            )
    elif message.photo:
        if len(state_message_id) == 1:
            await message.answer(
                text="Фотографии успешно загружены",
                reply_markup=keyboards.add_homework_in_kb(),
            )
    elif not message.photo and message.text:
        await message.answer(
            text="Текст успешно добавлен",
            reply_markup=keyboards.add_homework_in_kb(),
        )
    await state.set_state(AddHomework.add_descriptions_images)
    if message.photo:
        for idx, photo in enumerate(message.photo):
            if idx == len(message.photo) - 1:
                await bot_save_files(
                    bot,
                    "img",
                    "images",
                    photo,
                    message,
                    subject,
                    state,
                )


@rp.message(Command("new"))
async def command_add_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await add_homework_handler(message, state)


@rp.message(Command("stop"), AddHomeworkStateFilter)
async def command_stop_add_homework_handler(
    message: Message,
) -> None:
    await command_menu_handler(message)


@rp.callback_query(F.data.startswith("edit_homework_"))
async def edit_homework_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.start)
    await state.update_data({"homework_id": call.data.split("_")[-1]})
    await call.message.answer(
        text="Выберите действие:",
        reply_markup=keyboards.edit_homework_in_kb(),
    )


@rp.callback_query(F.data == "edit_hw_text", EditHomeworkStateFilter)
async def edit_homework_description_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.edit_text)
    data = await state.get_data()
    homework_data = await get_homework_from_id(
        telegram_id=call.message.chat.id,
        homework_id=data["homework_id"],
    )
    await call.message.answer(
        text=(
            f"Текущее описание:\n{homework_data['description']}\n\n"
            f"Введи новое описание:"
        ),
    )


@rp.message(EditHomework.edit_text)
async def save_edited_text_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.start)
    await message.answer(f"Новое описание:\n{message.text}")
    await state.update_data({"description": message.text})
    await message.answer(
        text="Выберите действие:",
        reply_markup=keyboards.edit_homework_in_kb(),
    )


@rp.callback_query(F.data == "edit_hw_save", EditHomeworkStateFilter)
async def save_edit_hw_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    response = await edit_hw_description(
        telegram_id=call.message.chat.id,
        homework_id=data["homework_id"],
        description=data["description"],
    )
    if response[0] == 200:
        await call.message.answer(
            text="Домашнее задание успешно обновлено",
            reply_markup=keyboards.to_edit_homework_in_kb(response[1]),
        )
    await state.clear()
    await command_menu_handler(call.message)


@rp.callback_query(F.data == "edit_hw_delete", EditHomeworkStateFilter)
async def delete_edit_hw_handler(
    call: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    status_code = await delete_homework(
        telegram_id=call.message.chat.id,
        homework_id=data["homework_id"],
    )
    if status_code == 200:
        await call.message.answer("Запись успешно удалена🗑️")
    await state.clear()
    await command_menu_handler(call.message)


@rp.message(Command("add_mailing"))
async def add_mailing(
    message: Message,
    state: FSMContext,
):
    if await check_for_admin(message.chat.id) == "superuser":
        await add_homework_handler(message, state, mailing=True)


@rp.callback_query(F.data == "delete_mailing")
async def delete_mailing_handler(
    call: CallbackQuery,
):
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/delete_mailing/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": call.message.chat.id,
        },
    )
    await call.message.answer("Запись успешно удалена🗑️")
    await call.message.delete()
    await command_menu_handler(call.message)
