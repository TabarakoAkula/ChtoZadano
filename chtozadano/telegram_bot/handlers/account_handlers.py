import asyncio
import datetime
import os

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from constants import DOCKER_URL
from filters import AccountStateFilter
from handlers.register_handlers import command_reset_handler
from keyboards import kb_menu
from keyboards.account import (
    account_become_admin,
    account_change_contacts,
    account_menu,
    account_settings,
)
import requests
from states import Account, ChangeContacts
from utils import check_for_admin

rp_account_router = Router()


@rp_account_router.message(F.text == "Аккаунт👤")
async def account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Account.start)
    if await check_for_admin(message.from_user.id) == "admin":
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=kb_menu.account_admin_page_rp_kb(),
        )
    else:
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=account_menu.account_user_page_rp_kb(),
        )


@rp_account_router.message(F.text == "Имя и Фамилия✏️", AccountStateFilter)
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
        reply_markup=account_change_contacts.change_contacts_rp_kb(),
    )


@rp_account_router.message(F.text == "Назад", AccountStateFilter)
async def redirect_to_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(Account.start)
    if await check_for_admin(message.from_user.id) == "admin":
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=kb_menu.account_admin_page_rp_kb(),
        )
    else:
        await message.answer(
            "Ты находишься в меню аккаунта",
            reply_markup=account_menu.account_user_page_rp_kb(),
        )


@rp_account_router.message(
    F.text == "Изменить данные📝",
    AccountStateFilter,
)
async def first_name_change_contacts_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(ChangeContacts.first_name)
    await message.answer(
        "Введи свое имя:",
    )


@rp_account_router.message(ChangeContacts.first_name)
async def last_name_change_contacts_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(first_name=message.text)
    await state.set_state(ChangeContacts.last_name)
    await message.answer(
        "Введи свою фамилию:",
    )


@rp_account_router.message(ChangeContacts.last_name)
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


@rp_account_router.message(Command("change_contacts"))
async def redirect_change_contacts(
    message: Message,
    state: FSMContext,
) -> None:
    await change_contacts_account_handler(message, state)


@rp_account_router.message(F.text == "Сменить класс🏫", AccountStateFilter)
async def change_class_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await command_reset_handler(message, state)


@rp_account_router.message(
    F.text == "Стать администратором👨‍💼",
    AccountStateFilter,
)
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
            reply_markup=kb_menu.account_admin_page_rp_kb(),
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
            reply_markup=account_become_admin.become_admin_rp_kb(),
        )


@rp_account_router.message(Command("become_admin"))
async def command_become_admin_account_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await become_admin_account_handler(message, state)


@rp_account_router.message(F.text == "Отправить заявку📁")
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


@rp_account_router.message(Command("show_become_admin"))
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
                reply_markup=account_become_admin.show_become_admin_in_kb(
                    user_id,
                ),
            )


@rp_account_router.callback_query(F.data == "become_admin_requests")
async def redirect_show_become_admin_handler(call: CallbackQuery) -> None:
    await command_show_become_admin_handler(call.message)


@rp_account_router.callback_query(
    F.data.startswith("decision_show_become_admin_"),
)
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


@rp_account_router.message(F.text == "Настройки🛠️")
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
        reply_markup=account_settings.settings_rp_kb(),
    )


@rp_account_router.message(
    F.text == "Сменить режим чата💬",
    AccountStateFilter,
)
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


@rp_account_router.message(
    F.text == "Сменить режим цитат📓",
    AccountStateFilter,
)
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


@rp_account_router.message(Command("settings"))
async def command_settings_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await settings_handler(message, state)
