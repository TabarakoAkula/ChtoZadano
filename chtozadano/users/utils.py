import asyncio
import datetime
import hashlib
import json
import os
import random
import string

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage
import dotenv

import users.models
from users.notifier import become_admin_notify, custom_notification


dotenv.load_dotenv()

BASE_DIR = settings.BASE_DIR
DjangoUser = get_user_model()


def create_password(a, b):
    md5_hashlib = hashlib.new("md5")
    md5_hashlib.update(str(a).encode())
    first_part = str(md5_hashlib.hexdigest())
    md5_hashlib.update(str(b).encode())
    second_part = str(md5_hashlib.hexdigest())
    return first_part + second_part


def confirmation_code_expired(db_time):
    datetime_now = datetime.datetime.now()
    delta = datetime_now - db_time
    return delta.total_seconds() / 60 > 60


def validate_password(password: str) -> tuple[bool, str]:
    special_symbols = ["$", "@", "#", "%"]
    if len(password) < 6:
        return False, "Длина пароля должна быть более 5 символов"
    if len(password) > 20:
        return False, "Длина пароля должна быть менее 21 символа"
    if not any(char.isdigit() for char in password):
        return False, "Пароль должен содержать цифры"
    if not any(char.isupper() for char in password):
        return False, "Пароль должен содержать заглавные буквы"
    if not any(char.islower() for char in password):
        return False, "Пароль должен содержать прописные буквы"
    if not any(char in special_symbols for char in password):
        return False, "Пароль должен содержать специальные символы"
    return True, ""


def new_become_admin_notify_management() -> None:
    if settings.USE_CELERY:
        celery_new_become_admin_notify.delay()
    else:
        new_become_admin_notify()


@shared_task()
def celery_new_become_admin_notify() -> None:
    return new_become_admin_notify()


def new_become_admin_notify() -> None:
    superusers = DjangoUser.objects.filter(
        is_superuser=True,
    ).values(
        "server_user__telegram_id",
    )
    if os.getenv("TEST"):
        return
    users_ids = [
        int(i["server_user__telegram_id"])
        for i in superusers
        if i["server_user__telegram_id"]
    ]
    number_of_requests = users.models.BecomeAdmin.objects.count()
    asyncio.run(
        become_admin_notify(
            number_of_requests=number_of_requests,
            users_ids=users_ids,
        ),
    )


def become_admin_decision_notify_management(
    new_admin_id: int,
    accept: bool,
) -> None:
    if settings.USE_CELERY:
        celery_become_admin_decision_notify.delay(new_admin_id, accept)
    else:
        become_admin_decision_notify(new_admin_id, accept)


@shared_task()
def celery_become_admin_decision_notify(
    new_admin_id: int,
    accept: bool,
) -> None:
    return become_admin_decision_notify(new_admin_id, accept)


def become_admin_decision_notify(
    new_admin_id: int,
    accept: bool,
) -> None:
    if os.getenv("TEST"):
        return
    text = (
        "Уведомление:\n"
        "Твоя заявка на становление администратором была отклонена❌"
    )
    if accept:
        text = (
            "Уведомление:\n"
            "Твоя заявка на становление администратором была одобрена✅"
        )
    asyncio.run(
        custom_notification(
            [new_admin_id],
            text,
            True,
        ),
    )


def get_randomized_name(name: str) -> str:
    random_chars = "".join(
        random.choices(string.ascii_letters + string.digits, k=5),
    )
    return f"{name}_{random_chars}"


def get_user_teachers(grade: int, letter: str) -> list | None:
    eng_teachers_url = staticfiles_storage.url("json/grades_subjects.json")
    with open(str(BASE_DIR) + eng_teachers_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        try:
            return json_data[str(grade)][letter]["teachers"]
        except KeyError:
            return None
