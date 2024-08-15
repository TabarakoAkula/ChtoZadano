import asyncio
import datetime
import json
import os
import pathlib
import urllib

from aiogram import html
import aiogram.exceptions
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
    response_data = json.loads(response.json())
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


async def send_images(images: list, caption: str, message: Message) -> None:
    photo_media_group = MediaGroupBuilder(caption=caption)
    for image in images:
        image_path = image["path"]
        tg_id = image["telegram_file_id"]
        try:
            if tg_id:
                photo_media_group.add_photo(media=tg_id)
            else:
                path = urllib.parse.unquote(image_path[1:])
                abs_path = pathlib.Path(path).resolve()
                photo_media_group.add_photo(FSInputFile(abs_path))
        except aiogram.exceptions.TelegramBadRequest:
            continue
    await message.answer_media_group(photo_media_group.build())


async def send_files(files: list, caption: str, message: Message) -> None:
    files_media_group = MediaGroupBuilder(caption=caption)
    for file in files:
        file_path = file["path"]
        tg_id = file["telegram_file_id"]
        try:
            if tg_id:
                files_media_group.add_document(media=tg_id)
            else:
                path = urllib.parse.unquote(file_path[1:])
                abs_path = pathlib.Path(path).resolve()
                files_media_group.add_document(FSInputFile(abs_path))
        except aiogram.exceptions.TelegramBadRequest:
            continue
    await message.answer_media_group(files_media_group.build())


async def generate_homework(
    homework: dict,
    record: int,
    message: Message,
) -> None:
    homework["subject"] = (
        homework["subject"][0].upper() + homework["subject"][1:]
    )
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
            await send_images(images, text, message)
        if files:
            if not images:
                caption = text
            else:
                caption = f"{homework['subject']}, добавленные файлы"
            await send_files(files, caption, message)
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
    filename: str,
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
    document,
    message,
    subject: str,
    state,
    file_name: str = "",
) -> None:
    if fs_type == "img":
        file_id = document.file_id
    else:
        file_id = document[1]
    file_info = await bot.get_file(file_id=file_id)
    file_path = file_info.file_path
    save_path = await get_file_path(
        file_path,
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
            f" добавлен т.к. вы не дождались его отправки",
        )
        return
    else:
        documents.append((save_path, file_id))
        if fs_type == "img":
            await state.update_data(images=documents)
        else:
            await message.answer(
                f"Файл {html.italic(file_name)} успешно добавлен",
            )
            await state.update_data(files=documents)


async def publish_homework(data: dict, telegram_id: int) -> None:
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
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + "/api/v1/add_homework/",
        json={
            "api_key": os.getenv("API_KEY"),
            "telegram_id": telegram_id,
            "description": data["text"],
            "subject": data["choose_subject"],
            "images": images_list,
            "files": files_list,
        },
    )
    return response.status_code
