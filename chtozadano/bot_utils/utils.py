import asyncio
import json
import os
import pathlib
import urllib

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
