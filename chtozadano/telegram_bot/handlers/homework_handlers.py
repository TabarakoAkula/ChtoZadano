import asyncio
import os

from aiogram import F, html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from bot_instance import bot
from constants import DOCKER_URL, SUBJECTS
import dotenv
from filters import (
    AddHomeworkFastDescriptionStateFilter,
    AddHomeworkSlowStateFilter,
    AddHwChooseSubjectStateFilter,
    EditHomeworkStateFilter,
    HomeworkStateFilter,
    PublishHomeworkStateFilter,
)
from handlers.menu_handlers import command_menu_handler
from keyboards.homework import (
    homework_add,
    homework_edit,
    homework_subject,
)
import redis
import requests
from states import AddHomeworkFast, AddHomeworkSlow, EditHomework
from utils import (
    bot_save_files,
    check_for_admin,
    delete_homework,
    edit_hw_description,
    generate_homework,
    get_fast_add,
    get_homework_from_id,
    get_user_subjects,
    publish_homework,
)

dotenv.load_dotenv()

USE_REDIS = os.getenv("USE_REDIS")

if USE_REDIS:
    REDIS_BOT_URL = os.getenv("REDIS_BOT_URL")
    redis_client = redis.from_url(REDIS_BOT_URL)

rp_homework_router = Router()


@rp_homework_router.message(F.text == "Добавить📋", HomeworkStateFilter)
async def add_homework_handler(
    message: Message,
    state: FSMContext,
    mailing: bool = False,
    for_class: bool = True,
) -> None:
    fast_add_bool = await get_fast_add(message.chat.id)
    if fast_add_bool:
        await state.set_state(AddHomeworkSlow.choose_subject)
    else:
        await state.set_state(AddHomeworkFast.choose_subject)
    await state.update_data(fast_add_bool=fast_add_bool)
    subjects = await get_user_subjects(message.chat.id)
    try:
        subjects.append("информация")
    except AttributeError:
        await message.answer(
            "Для взаимодействия с ботом необходимо зарегистрироваться."
            " Введи команду /start",
        )
        return
    keyboard = homework_subject.homework_subject_in_kb(
        subjects=subjects,
        add=True,
    )
    text = "Выбери предмет, по которому хочешь добавить домашку"
    if mailing and not for_class:
        keyboard = homework_add.get_mailings()
        text = "Выбери уровень рассылки"
    elif mailing and for_class:
        await state.update_data(choose_subject="информация")
        if fast_add_bool:
            await state.set_state(AddHomeworkFast.add_data)
            await message.answer(
                text="Отлично, теперь отправь домашку\n"
                "(Если необходимо добавить файлы - отправь сначала их)",
            )
        else:
            await state.set_state(AddHomeworkSlow.add_descriptions_images)
            await message.answer(
                text="Отлично, теперь отправь домашку\n(Ты можешь отправить"
                " изображения и описание, файлы можно будет отправить позже)",
            )
        return
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )


@rp_homework_router.message(Command("info"))
async def add_class_info_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await add_homework_handler(
        message,
        state,
        mailing=True,
        for_class=True,
    )


@rp_homework_router.callback_query(
    F.data.startswith("add_hw_subject_"),
    AddHwChooseSubjectStateFilter,
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
    await call.answer(f"Выбранный предмет: {subject}")
    data = await state.get_data()
    if data["fast_add_bool"]:
        await state.set_state(AddHomeworkFast.add_data)
        await call.message.answer(
            text="Отлично, теперь отправь домашку\n"
            "(Если необходимо добавить файлы - отправь сначала их)",
        )
    else:
        await state.set_state(AddHomeworkSlow.add_descriptions_images)
        await call.message.answer(
            text="Отлично, теперь отправь домашку\n(Ты можешь отправить"
            " изображения и описание, файлы можно будет отправить позже)",
        )


async def send_message_after_delay(
    chat_id: int,
    state: FSMContext,
    message: Message = "",
    publish: bool = False,
) -> None:
    await asyncio.sleep(3)
    await state.set_state(AddHomeworkFast.add_descriptions_images)
    if not publish:
        data = await state.get_data()
        number_of_files = len(data["files"])
        if number_of_files == 1:
            files_text = "файл"
        elif 4 <= number_of_files <= 2:
            files_text = "файла"
        else:
            files_text = "файлов"
        await bot.send_message(
            chat_id=chat_id,
            text=f"Ты добавил {number_of_files} {files_text}.\n"
            f"Теперь отправь описание и изображения, если нужно",
        )
    else:
        await command_publish_hw_handler(message, state)


def set_timer(user_id: int):
    redis_client.setex(f"timer_{user_id}", 3, "active")


def cancel_timer(user_id: int):
    redis_client.delete(f"timer_{user_id}")


def check_timer(user_id: int):
    return redis_client.get(f"timer_{user_id}")


@rp_homework_router.message(
    F.content_type.in_([ContentType.DOCUMENT, ContentType.AUDIO]),
    AddHomeworkFast.add_data,
)
async def fast_add_homework_data_handler(
    message: Message,
    state: FSMContext,
) -> None:
    state_data = await state.get_data()
    subject = state_data["choose_subject"]
    if message.document:
        for idx, document in enumerate(message.document):
            if document[0] == "file_id":
                await bot_save_files(
                    bot,
                    "files",
                    "files",
                    document,
                    message,
                    subject,
                    state,
                    message.document.file_name,
                    show_message=False,
                )
    if message.audio:
        for idx, music in enumerate(message.audio):
            if music[0] == "file_id":
                await bot_save_files(
                    bot,
                    "music",
                    "files",
                    music,
                    message,
                    subject,
                    state,
                    message.audio.file_name,
                    show_message=False,
                )
    if not USE_REDIS:
        dp = await state.get_data()
        try:
            dp["delay_task"].cancel()
        except KeyError:
            pass
        await state.update_data(
            delay_task=asyncio.create_task(
                send_message_after_delay(message.chat.id, state),
            ),
        )
    else:
        user_id = message.from_user.id
        if check_timer(user_id):
            cancel_timer(user_id)
        set_timer(user_id)
        await asyncio.sleep(3)
        if not check_timer(user_id):
            await message.answer(
                text="Теперь отправь описание и изображения, если нужно",
            )


@rp_homework_router.message(
    F.content_type.in_([ContentType.PHOTO, ContentType.TEXT]),
    AddHomeworkFastDescriptionStateFilter,
)
async def fast_add_homework_description_images_handler(
    message: Message,
    state: FSMContext,
) -> None:
    text = message.caption or message.text
    if text:
        await state.update_data(text=text)
    state_data = await state.get_data()
    subject = state_data["choose_subject"]
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
    if not USE_REDIS:
        dp = await state.get_data()
        try:
            dp["delay_task"].cancel()
        except KeyError:
            pass
        await state.update_data(
            delay_task=asyncio.create_task(
                send_message_after_delay(
                    message.chat.id,
                    state,
                    message,
                    publish=True,
                ),
            ),
        )
    else:
        user_id = message.from_user.id
        if check_timer(user_id):
            cancel_timer(user_id)
        set_timer(user_id)
        await asyncio.sleep(3)
        if not check_timer(user_id):
            await command_publish_hw_handler(message, state)


@rp_homework_router.callback_query(
    F.data == "add_homework_files",
    AddHomeworkSlowStateFilter,
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
    await state.set_state(AddHomeworkSlow.add_files)


@rp_homework_router.message(
    AddHomeworkSlow.add_files,
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
    AddHomeworkSlow.add_descriptions_images,
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
    try:
        text = data["text"]
    except KeyError:
        text = ""
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
    await state.set_state(AddHomeworkSlow.add_descriptions_images)
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


@rp_homework_router.callback_query(F.data.startswith("edit_homework_"))
async def edit_homework_handler(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(EditHomework.start)
    await state.update_data({"homework_id": call.data.split("_")[-1]})
    await call.message.answer(
        text="Выбери действие:",
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
        text="Выбери действие:",
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
        await add_homework_handler(
            message,
            state,
            mailing=True,
            for_class=False,
        )


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


@rp_homework_router.message(F.content_type.in_([ContentType.TEXT]))
async def enter_subject_handler(
    message: Message,
) -> None:
    mess_text = message.text.lower()
    subject = str()
    for sub in SUBJECTS:
        if sub in mess_text:
            subject = sub
            break

    if subject == "":
        await message.answer("Я не знаю такого предмета")
        return
    if subject != "info":
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/get_homework_for_subject/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": message.chat.id,
                "subject": SUBJECTS[subject],
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
