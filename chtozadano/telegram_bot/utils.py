import asyncio
import datetime
import os
import pathlib
import urllib

from aiogram import html
import aiogram.exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder
import dotenv
import requests

dotenv.load_dotenv()

DOCKER_URL = os.getenv("DOCKER_URL")


async def check_for_admin(telegram_id: int) -> str:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/is_user_admin/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    response_data = response.json()
    admin = response_data["is_admin"]
    superuser = response_data["is_superuser"]
    if not admin and not superuser:
        return "user"
    if admin and not superuser:
        return "admin"
    if superuser:
        return "superuser"
    return "Undefined"


async def delete_become_admin(telegram_id: int) -> None:
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/become_admin_delete_user/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    return


async def send_images(
    images: list,
    caption: str,
    message: Message,
    telegram_id: int,
    homework_id: int,
) -> None:
    photo_media_group = MediaGroupBuilder(caption=caption)
    all_images_id, images_with_id = set(), set()
    for image in images:
        image_path = image["path"]
        tg_id = image["telegram_file_id"]
        try:
            if tg_id:
                photo_media_group.add_photo(media=tg_id)
                images_with_id.add(tg_id)
            else:
                path = urllib.parse.unquote(image_path[1:])
                abs_path = pathlib.Path(path).resolve()
                photo_media_group.add_photo(FSInputFile(abs_path))
        except aiogram.exceptions.TelegramBadRequest:
            continue
    response = await message.answer_media_group(photo_media_group.build())
    for message in response:
        all_images_id.add(message.photo[-1].file_id)
    images_without_id = all_images_id - images_with_id
    await add_documents_file_id(
        telegram_id,
        homework_id,
        "img",
        list(images_without_id),
    )


async def send_files(
    files: list,
    caption: str,
    message: Message,
    telegram_id: int,
    homework_id: int,
) -> None:
    files_media_group = MediaGroupBuilder(caption=caption)
    all_files_id, files_with_id = set(), set()
    for file in files:
        file_path = file["path"]
        tg_id = file["telegram_file_id"]
        try:
            if tg_id:
                files_media_group.add_document(media=tg_id)
                files_with_id.add(tg_id)
            else:
                path = urllib.parse.unquote(file_path[1:])
                abs_path = pathlib.Path(path).resolve()
                files_media_group.add_document(FSInputFile(abs_path))
        except aiogram.exceptions.TelegramBadRequest:
            continue
    response = await message.answer_media_group(files_media_group.build())
    for message in response:
        all_files_id.add(message.document.file_id)
    files_without_id = all_files_id - files_with_id
    await add_documents_file_id(
        telegram_id,
        homework_id,
        "file",
        list(files_without_id),
    )


async def generate_mailing(
    homework: dict,
    message: Message,
) -> None:
    counter = 0
    for row in homework:
        mailing = homework[row]
        try:
            if not mailing["group"]:
                continue
        except TypeError:
            continue
        counter += 1
        level = ""
        if row == "class":
            level = "Информация для класса"
        elif row == "admins":
            level = "Информация для администрации"
        elif row == "school":
            level = "Информация для школы"
        text = f"{level}, {mailing['author']}:\n{mailing['description']}"
        images = mailing["images"]
        files = mailing["files"]
        if images or files:
            if images:
                await send_images(
                    images,
                    text,
                    message,
                    message.chat.id,
                    mailing["id"],
                )
            if files:
                if not images:
                    caption = text
                else:
                    caption = f"{mailing['subject']}, добавленные файлы"
                await send_files(
                    files,
                    caption,
                    message,
                    message.chat.id,
                    mailing["id"],
                )
        else:
            await message.answer(text)
    if counter == 0:
        await message.answer("Новой информации пока что нет")


async def generate_homework(
    homework: dict,
    record: int,
    message: Message,
) -> None:
    homework["subject"] = (
        homework["subject"][0].upper() + homework["subject"][1:]
    )
    if homework["subject"] == "Информация":
        await generate_mailing(homework, message)
        return
    try:
        group = homework["group"]
    except KeyError:
        if record != 0:
            await message.answer(
                text=f"{record}: {homework['subject']}:\nНичего не задано",
            )
            return
        await message.answer(
            text=f"{homework['subject']}:\nНичего не задано",
        )
        return
    if group != 0:
        text = (
            f"{record}: {homework['subject']},"
            f" {homework['group']} группа, {homework['author']}:\n"
            f"{homework['description']}"
        )
    else:
        text = (
            f"{record}: {homework['subject']},"
            f" {homework['author']}:\n"
            f"{homework['description']}"
        )
    if record == 0:
        text = text[2:]
    images = homework["images"]
    files = homework["files"]
    if images or files:
        if images:
            await send_images(
                images,
                text,
                message,
                message.chat.id,
                homework["id"],
            )
        if files:
            if not images:
                caption = text
            else:
                caption = f"{homework['subject']}, добавленные файлы"
            await send_files(
                files,
                caption,
                message,
                message.chat.id,
                homework["id"],
            )
    else:
        await message.answer(text)


async def get_user_subjects(telegram_id: int) -> list:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_user_subjects/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    return response.json()


async def get_file_path(
    file_type: str,
    subject: str,
    telegram_id: int,
    file_id: int,
    extension: str,
) -> str:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_abbreviation/",
        json={
            "api_key": os.getenv("API_KEY"),
            "subject": subject,
            "telegram_id": telegram_id,
        },
    )
    response = response.json()
    today = datetime.datetime.today()
    month = today.month
    if month < 10:
        month = f"0{month}"
    day = today.day
    if day < 10:
        day = f"0{day}"
    save_directory = (
        f"media/homework/{file_type}/{today.year}/{month}/"
        f"{response['grade']}/{response['letter']}/{day}/"
        f"{response['abbreviation']}/"
    )
    return save_directory + f"{telegram_id}_{file_id[:20]}{extension}"


async def bot_save_files(
    bot: aiogram.Bot,
    fs_type: str,
    state_type: str,
    document: any,
    message: Message,
    subject: str,
    state: FSMContext,
    file_name: str = "",
    show_message: bool = True,
) -> None:
    if fs_type == "img":
        file_id = document.file_id
    else:
        file_id = document[1]
    file_info = await bot.get_file(file_id=file_id)
    file_path = file_info.file_path
    save_path = await get_file_path(
        fs_type,
        subject,
        message.chat.id,
        file_id,
        os.path.splitext(file_path)[1],
    )
    path = pathlib.Path(save_path[: save_path.rfind("/")])
    path.mkdir(exist_ok=True, parents=True)
    await bot.download_file(file_path, save_path)
    state_data = await state.get_data()
    try:
        documents = state_data[state_type]
    except KeyError:
        await message.answer(
            f"Файл {html.italic(file_name)} не был"
            f" добавлен т.к. ты не дождались его отправки",
        )
        return
    else:
        documents.append((save_path, file_id))
        if fs_type == "img":
            await state.update_data(images=documents)
        else:
            if show_message:
                await message.answer(
                    f"Файл {html.italic(file_name)} успешно добавлен",
                )
            await state.update_data(files=documents)


async def publish_homework(data: dict, telegram_id: int) -> tuple[int, int]:
    images_list = []
    files_list = []
    try:
        for image_tuple in data["images"]:
            path = image_tuple[0]
            images_list.append(
                {
                    "path": path[path.find("/") + 1 :],
                    "telegram_file_id": image_tuple[1],
                },
            )
    except KeyError:
        pass
    try:
        for file_tuple in data["files"]:
            path = file_tuple[0]
            files_list.append(
                {
                    "path": path[path.find("/") + 1 :],
                    "telegram_file_id": file_tuple[1],
                },
            )
    except KeyError:
        pass
    mailing = False
    subject = data["choose_subject"]
    if subject.lower() in [
        "информация",
        "adminsinfo",
        "schoolinfo",
    ]:
        mailing = True
    try:
        text = data["text"]
    except KeyError:
        text = ""
    if not mailing:
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/add_homework/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": telegram_id,
                "description": text,
                "subject": subject,
                "images": images_list,
                "files": files_list,
            },
        )
        homework_id = response.json()["homework_id"]
    else:
        level = "class"
        if subject == "adminsinfo":
            level = "admins"
        elif subject == "schoolinfo":
            level = "school"
        response = await asyncio.to_thread(
            requests.post,
            url=DOCKER_URL + "/api/v1/add_mailing/",
            json={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": telegram_id,
                "description": text,
                "level": level,
                "images": images_list,
                "files": files_list,
            },
        )
        homework_id = -1
    return response.status_code, homework_id


async def get_homework_from_id(telegram_id: int, homework_id: int) -> dict:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_homework_from_id/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "homework_id": homework_id,
        },
    )
    return response.json()


async def edit_hw_description(
    telegram_id: int,
    homework_id: int,
    description: str,
) -> tuple[int, int]:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/edit_homework_description/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "homework_id": homework_id,
            "description": description,
        },
    )
    return response.status_code, homework_id


async def delete_homework(
    telegram_id: int,
    homework_id: int,
) -> int:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/delete_homework/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "homework_id": homework_id,
        },
    )
    return response.status_code


async def get_homework_from_date(telegram_id: int, date: int) -> dict:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_homework_from_date/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "date": date,
        },
    )
    return response.json()


async def add_documents_file_id(
    telegram_id: int,
    homework_id: int,
    document_type: str,
    document_ids: list[str],
) -> None:
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/add_files_ids/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "homework_id": homework_id,
            "document_type": document_type,
            "document_ids": document_ids,
        },
    )
    return


async def get_fast_add(telegram_id: int) -> bool | str:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/get_fast_add/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
        },
    )
    try:
        return response.json()["fast_hw"]
    except KeyError:
        return "Error"
