import os
import pathlib
import urllib

from aiogram import Bot, html
from aiogram.client.session.aiohttp import AiohttpSession
import aiogram.exceptions
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

import homework.models

load_dotenv()


async def homework_notifier(
    users_ids: list[int],
    telegram_id: int,
    homework_data: dict,
) -> None:
    bot_session = AiohttpSession()
    notify_bot = Bot(token=os.getenv("BOT_TOKEN"), session=bot_session)
    homework_data["subject"] = (
        homework_data["subject"][0].upper() + homework_data["subject"][1:]
    )
    if homework_data["subject"] == "Информация":
        await mailing_generator(
            homework_data,
            notify_bot,
            users_ids,
            telegram_id,
        )
        await bot_session.close()
        return
    try:
        group = homework_data["group"]
    except KeyError:
        text = f"{homework_data['subject']}:\nНичего не задано"
        for user_id in users_ids:
            await notify_bot.send_message(text=text, chat_id=user_id)
        return
    if group != 0:
        text = (
            f"{homework_data['subject']},"
            f" {homework_data['group']} группа, {homework_data['author']}:\n"
            f"{homework_data['description']}"
        )
    else:
        text = (
            f"{homework_data['subject']},"
            f" {homework_data['author']}:\n"
            f"{homework_data['description']}"
        )
    images = homework_data["images"]
    files = homework_data["files"]
    if images or files:
        if images:
            await send_images(
                images,
                text,
                notify_bot,
                users_ids,
                homework_data["id"],
            )
        if files:
            if not images:
                caption = text
            else:
                caption = f"{homework_data['subject']}, добавленные файлы"
            await send_files(
                files,
                caption,
                notify_bot,
                users_ids,
                homework_data["id"],
            )
    else:
        for user in users_ids:
            await notify_bot.send_message(
                text=text,
                chat_id=user,
            )
    await bot_session.close()
    return


async def mailing_generator(
    mailing: dict,
    bot: Bot,
    users_ids: list,
    telegram_id: int,
) -> None:
    if mailing["group"] == -1:
        level = html.bold("Информация для класса")
    elif mailing["group"] == -2:
        level = html.bold("Информация для администрации")
    else:
        level = html.bold("Информация для школы")
    text = f"{level}, {mailing['author']}:\n{mailing['description']}"
    images = mailing["images"]
    files = mailing["files"]
    if images or files:
        if images:
            await send_images(
                images,
                text,
                bot,
                users_ids,
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
                bot,
                users_ids,
                mailing["id"],
            )
    else:
        for user_id in users_ids:
            await bot.send_message(
                text=text,
                chat_id=user_id,
            )
    return


async def send_images(
    images: list,
    caption: str,
    bot: Bot,
    users_ids: list,
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
    media_group_build = photo_media_group.build()
    response = []
    for user_id in users_ids:
        response = await bot.send_media_group(
            media=media_group_build,
            chat_id=user_id,
        )
    for message in response:
        all_images_id.add(message.photo[-1].file_id)
    images_without_id = all_images_id - images_with_id
    await add_documents_file_id(
        homework_id=homework_id,
        document_type="img",
        document_ids=list(images_without_id),
    )


async def send_files(
    files: list,
    caption: str,
    bot: Bot,
    user_ids: list,
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
    media_group_build = files_media_group.build()
    response = []
    for user_id in user_ids:
        response = await bot.send_media_group(
            media=media_group_build,
            chat_id=user_id,
        )
    for message in response:
        all_files_id.add(message.document.file_id)
    files_without_id = all_files_id - files_with_id
    await add_documents_file_id(
        homework_id=homework_id,
        document_type="file",
        document_ids=list(files_without_id),
    )


async def add_documents_file_id(
    homework_id: int,
    document_type: str,
    document_ids: list[str],
) -> None:
    homework_obj = await sync_to_async(
        homework.models.Homework.objects.filter(id=homework_id)
        .prefetch_related("images", "files")
        .first,
    )()

    if document_type == "img":
        document_objects = await sync_to_async(list)(homework_obj.images.all())
    else:
        document_objects = await sync_to_async(list)(homework_obj.files.all())

    for index, document in enumerate(document_objects):
        document.telegram_file_id = document_ids[index]
        await sync_to_async(document.save)()

    return
