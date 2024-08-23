import asyncio
import os

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from bot_instance import bot
from constants import DOCKER_URL, SUBJECTS
from filters import (
    AddHomeworkStateFilter,
    EditHomeworkStateFilter,
    HomeworkStateFilter,
    PublishHomeworkStateFilter,
)
from handlers.menu_handlers import command_menu_handler
from keyboards.homework import (
    homework_add,
    homework_edit,
    homework_menu,
    homework_subject,
)
import requests
from states import AddHomework, EditHomework, Homework
from utils import (
    bot_save_files,
    check_for_admin,
    delete_homework,
    edit_hw_description,
    generate_homework,
    get_homework_from_date,
    get_homework_from_id,
    get_user_subjects,
    publish_homework,
)

rp_homework_router = Router()


@rp_homework_router.message(F.text == "Домашка📝")
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


@rp_homework_router.message(
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


@rp_homework_router.message(Command("tomorrow"))
async def command_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await tomorrow_homework_handler(message, state)


@rp_homework_router.message(
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


@rp_homework_router.callback_query(
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


@rp_homework_router.message(Command("subject"))
async def command_redirect_homework_subject(
    message: Message,
    state: FSMContext,
) -> None:
    await get_subject_hw_handler(message, state)


@rp_homework_router.message(F.text.lower().in_(SUBJECTS))
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


@rp_homework_router.message(F.text == "Найти домашку🔎", HomeworkStateFilter)
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


@rp_homework_router.message(F.text == "Назад", HomeworkStateFilter)
async def return_to_homework(
    message: Message,
    state: FSMContext,
) -> None:
    await homework_handler(message, state)


@rp_homework_router.message(Homework.find)
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


@rp_homework_router.message(Command("date"))
async def command_search_hw_handler(
    message: Message,
    state: FSMContext,
):
    await search_homework_handler(message, state)


@rp_homework_router.message(F.text == "Добавить📋", HomeworkStateFilter)
async def add_homework_handler(
    message: Message,
    state: FSMContext,
    mailing: bool = False,
) -> None:
    await state.set_state(AddHomework.choose_subject)
    subjects = await get_user_subjects(message.chat.id)
    subjects.append("информация")
    keyboard = homework_subject.homework_subject_in_kb(
        subjects=subjects,
        add=True,
    )
    text = "Выбери предмет, по которому хочешь добавить домашку"
    if mailing:
        keyboard = homework_add.get_mailings()
        text = "Выбери уровень рассылки"
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )


@rp_homework_router.callback_query(
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


@rp_homework_router.callback_query(
    F.data == "add_homework_files",
    AddHomeworkStateFilter,
)
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
        reply_markup=homework_add.add_homework_maximum_in_kb(),
    )
    await state.set_state(AddHomework.add_files)


@rp_homework_router.message(
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


@rp_homework_router.callback_query(F.data == "publish_hw")
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
                reply_markup=homework_edit.to_edit_homework_in_kb(
                    homework_id,
                ),
            )
        else:
            await call.message.answer(
                text="Информация успешно опубликована",
                reply_markup=homework_edit.delete_mailing_in_kb(),
            )
    await state.clear()
    await command_menu_handler(call.message)


@rp_homework_router.message(Command("publish"), PublishHomeworkStateFilter)
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
                reply_markup=homework_edit.to_edit_homework_in_kb(
                    homework_id,
                ),
            )
        else:
            await message.answer(
                text="Информация успешно опубликована",
                reply_markup=homework_edit.delete_mailing_in_kb(),
            )
    await state.clear()
    await command_menu_handler(message)


@rp_homework_router.message(
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
                reply_markup=homework_add.add_homework_in_kb(),
            )
    elif message.photo:
        if len(state_message_id) == 1:
            await message.answer(
                text="Фотографии успешно загружены",
                reply_markup=homework_add.add_homework_in_kb(),
            )
    elif not message.photo and message.text:
        await message.answer(
            text="Текст успешно добавлен",
            reply_markup=homework_add.add_homework_in_kb(),
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


@rp_homework_router.message(Command("new"))
async def command_add_homework_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await add_homework_handler(message, state)


@rp_homework_router.message(Command("stop"), AddHomeworkStateFilter)
async def command_stop_add_homework_handler(
    message: Message,
) -> None:
    await command_menu_handler(message)


@rp_homework_router.callback_query(F.data.startswith("edit_homework_"))
async def edit_homework_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.start)
    await state.update_data({"homework_id": call.data.split("_")[-1]})
    await call.message.answer(
        text="Выберите действие:",
        reply_markup=homework_edit.edit_homework_in_kb(),
    )


@rp_homework_router.callback_query(
    F.data == "edit_hw_text",
    EditHomeworkStateFilter,
)
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


@rp_homework_router.message(EditHomework.edit_text)
async def save_edited_text_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.start)
    await message.answer(f"Новое описание:\n{message.text}")
    await state.update_data({"description": message.text})
    await message.answer(
        text="Выберите действие:",
        reply_markup=homework_edit.edit_homework_in_kb(),
    )


@rp_homework_router.callback_query(
    F.data == "edit_hw_save",
    EditHomeworkStateFilter,
)
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
            reply_markup=homework_edit.to_edit_homework_in_kb(
                response[1],
            ),
        )
    await state.clear()
    await command_menu_handler(call.message, False)


@rp_homework_router.callback_query(
    F.data == "edit_hw_delete",
    EditHomeworkStateFilter,
)
async def delete_edit_hw_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    status_code = await delete_homework(
        telegram_id=call.message.chat.id,
        homework_id=data["homework_id"],
    )
    if status_code == 200:
        await call.message.answer("Запись успешно удалена🗑️")
    await state.clear()
    await command_menu_handler(call.message, False)


@rp_homework_router.message(Command("add_mailing"))
async def add_mailing(
    message: Message,
    state: FSMContext,
) -> None:
    if await check_for_admin(message.chat.id) == "superuser":
        await add_homework_handler(message, state, mailing=True)


@rp_homework_router.callback_query(F.data == "delete_mailing")
async def delete_mailing_handler(
    call: CallbackQuery,
) -> None:
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
    await command_menu_handler(call.message, False)
