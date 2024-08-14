import asyncio
import json
import os
import pathlib
import urllib

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


async def generate_homework(homework: dict, record: int, message: Message):
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
            photo_media_group = MediaGroupBuilder(caption=text)
            for image in homework["images"]:
                path = urllib.parse.unquote(image[1:])
                abs_path = pathlib.Path(path).resolve()
                photo_media_group.add_photo(FSInputFile(abs_path))
            await message.answer_media_group(photo_media_group.build())
        if files:
            if not images:
                caption = text
            else:
                caption = (
                    f"Добавленные файлы к домашке по {homework['subject']}"
                )
            files_media_group = MediaGroupBuilder(caption=caption)
            for file in homework["files"]:
                path = urllib.parse.unquote(file[1:])
                abs_path = pathlib.Path(path).resolve()
                files_media_group.add_document(FSInputFile(abs_path))
            await message.answer_media_group(files_media_group.build())
    else:
        await message.answer(text)
