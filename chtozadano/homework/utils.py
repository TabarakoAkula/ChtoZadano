import datetime
import json
import os
import random

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage
import django.db.models
from django.db.models import Q
from django.http import request as type_request
from django.shortcuts import redirect
import dotenv

from homework.api.serializers import HomeworkSerializer
import homework.models
from homework.notifier import custom_notification, homework_notifier
import users.models

dotenv.load_dotenv()

BASE_DIR = settings.BASE_DIR
DjangoUser = get_user_model()


def get_user_subjects(grade: int, letter: str, group: int) -> list:
    grades_subjects_url = staticfiles_storage.url("json/grades_subjects.json")
    subjects_url = staticfiles_storage.url("json/subjects.json")
    with open(
        str(BASE_DIR) + grades_subjects_url,
        encoding="utf-8",
    ) as data:
        json_data = json.loads(data.read())
        try:
            user_subjects = json_data[str(grade)][letter]["subject_codes"]
        except KeyError:
            return [
                {
                    "grade": grade,
                    "letter": letter,
                },
            ]
        with open(
            str(BASE_DIR) + subjects_url,
            encoding="utf-8",
        ) as subjects_data:
            json_subject_data = json.loads(subjects_data.read())
            response = []
            user_subjects.append("class")
            user_subjects.append("phys-c")
            for i in user_subjects:
                if i in ["eng1", "eng2", "ger1", "ger2", "ikt1", "ikt2"]:
                    i_group = int(i[-1:])
                    if i_group != group:
                        continue
                    if isinstance(json_subject_data[i], list):
                        response.append(json_subject_data[i][0].lower())
                    else:
                        response.append(json_subject_data[i].lower())
                else:
                    if isinstance(json_subject_data[i], list):
                        response.append(json_subject_data[i][0].lower())
                    else:
                        response.append(json_subject_data[i].lower())
    return response


def get_user_subjects_abbreviation(grade: int, letter: str) -> list:
    grades_subjects_url = staticfiles_storage.url("json/grades_subjects.json")
    with open(str(BASE_DIR) + grades_subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        return json_data[str(grade)][letter]["subject_codes"]


def get_abbreviation_from_name(name: str) -> str:
    subjects_url = staticfiles_storage.url("json/subjects.json")
    with open(str(BASE_DIR) + subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        for i in json_data:
            if isinstance(json_data[i], list):
                for j in range(len(json_data[i])):
                    if json_data[i][j].lower() == name.lower():
                        return i
            elif json_data[i].lower() == name.lower():
                return i
    return "ERROR"


def get_name_from_abbreviation(abbreviation: str) -> str:
    subjects_url = staticfiles_storage.url("json/subjects.json")
    with open(str(BASE_DIR) + subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        response_object = json_data[abbreviation]
        if isinstance(response_object, list):
            return response_object[0]
        return response_object


def save_files(
    request_files_list: list,
    grade: int,
    letter: str,
    subject: str,
) -> tuple[str, list] | tuple[str, str]:
    today = datetime.date.today()
    month = today.month
    day = today.day
    if month < 10:
        month = f"0{month}"
    if day < 10:
        day = f"0{day}"
    today_path = f"{today.year}/{month}/{grade}/{letter}/{day}/{subject}/"
    files_list_for_model = []
    for r_file in request_files_list:
        file_extension = r_file.name.split(".")[-1]
        if file_extension.lower() in ["png", "jpeg", "jpg"]:
            file_name = default_storage.save(
                f"homework/img/{today_path}/{r_file.name}",
                r_file,
            )
            if len(file_name) >= 100:
                file_name = (
                    file_name[:50] + "_" + str(random.getrandbits(128))[:40]
                )
            files_list_for_model.append((file_name, "img"))
        elif file_extension.lower() in [
            "pdf",
            "ppt",
            "pptx",
            "doc",
            "docx",
            "zip",
        ]:
            file_name = default_storage.save(
                f"homework/files/{today_path}/{r_file.name}",
                r_file,
            )
            if len(file_name) >= 100:
                file_name = (
                    file_name[:50] + "_" + str(random.getrandbits(128))[:40]
                )
            files_list_for_model.append((file_name, "file"))
        elif file_extension.lower() in ["mp3", "ogg", "acc", "wav"]:
            file_name = default_storage.save(
                f"homework/music/{today_path}/{r_file.name}",
                r_file,
            )
            if len(file_name) >= 100:
                file_name = (
                    file_name[:50] + "_" + str(random.getrandbits(128))[:40]
                )
            files_list_for_model.append((file_name, "music"))
        else:
            return "Error", file_extension
    return "Ok", files_list_for_model


def get_all_homework_from_grade(
    grade: int,
    letter: str,
) -> django.db.models.QuerySet:
    return homework.models.Homework.objects.filter(
        grade=grade,
        letter=letter,
    ).all()


def get_tomorrow_schedule(
    grade: int,
    letter: str,
    group: int,
) -> django.db.models.QuerySet:
    today = datetime.datetime.today()
    weekday = today.weekday() + 2
    if weekday > 7:
        weekday -= 7
    if weekday == 7:
        weekday = 1
    return (
        homework.models.Schedule.objects.filter(
            grade=grade,
            letter=letter,
            weekday=weekday,
        )
        .filter(Q(group=group) | Q(group=0))
        .order_by("lesson")
        .all()
    )


def get_schedule_from_weekday(
    grade: int,
    letter: str,
    group: int,
    weekday: int,
) -> django.db.models.QuerySet:
    return (
        homework.models.Schedule.objects.filter(
            grade=grade,
            letter=letter,
            weekday=weekday,
        )
        .filter(Q(group=group) | Q(group=0))
        .order_by("lesson")
        .all()
    )


def get_list_of_dates(grade: int) -> dict:
    weekday_full = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
    }
    today = datetime.datetime.now()
    today_date = today.date()
    date_list = {}
    if today.hour <= 15:
        week_range = range(0, 7)
    else:
        week_range = range(1, 8)
    for day in week_range:
        date = today_date + datetime.timedelta(days=day)
        if not (
            date.weekday() == 6 or (int(grade) < 6 and date.weekday() == 5)
        ):
            date_list[date.weekday()] = (
                f"{weekday_full[date.weekday() + 1]},"
                f" {date.strftime('%d.%m')}"
            )
    return date_list


def check_grade_letter(request: type_request) -> tuple[str, list]:
    if request.user.is_authenticated:
        grade = request.user.server_user.grade
        letter = request.user.server_user.letter
        group = request.user.server_user.group
    else:
        try:
            data = json.loads(request.COOKIES.get("hw_data"))
        except TypeError:
            messages.error(
                request,
                "Сначала необходимо выбрать в каком тыклассе",
            )
            return "Error", redirect("homework:choose_grad_let")
        grade = data["grade"]
        letter = data["letter"]
        group = data["group"]
        if not grade or not letter:
            messages.error(
                request,
                "Сначала необходимо выбрать в каком тыклассе",
            )
            return "Error", redirect("homework:choose_grad_let")
    return "Successful", [grade, letter, group]


def add_documents_file_id(
    homework_id: int,
    document_type: str,
    document_ids: list[str],
    grade: int = None,
    telegram_id: int = None,
) -> None:
    if telegram_id:
        user = users.models.User.objects.get(telegram_id=telegram_id)
        grade = user.grade
    homework_obj = (
        homework.models.Homework.objects.filter(id=homework_id, grade=grade)
        .prefetch_related("images", "files")
        .first()
    )
    if document_type == "img":
        document_objects = homework_obj.images.all()
    else:
        document_objects = homework_obj.files.all()
    for index, document in enumerate(document_objects):
        document.telegram_file_id = document_ids[index]
        document.save()
    return


async def add_notification(
    model_object,
    user,
    use_groups: bool = False,
) -> None:
    if use_groups:
        users_ids = await sync_to_async(list)(
            users.models.User.objects.filter(
                grade=user.grade,
                letter=user.letter,
                group=user.group,
                chat_mode=True,
            ).values("telegram_id"),
        )
    else:
        users_ids = await sync_to_async(list)(
            users.models.User.objects.filter(
                grade=user.grade,
                letter=user.letter,
                chat_mode=True,
            ).values("telegram_id"),
        )
    model_object.subject = get_name_from_abbreviation(model_object.subject)
    users_ids = [i["telegram_id"] for i in users_ids]
    serializer = HomeworkSerializer(model_object)
    serialized_data = await sync_to_async(lambda: serializer.data)()
    users_ids = [i for i in users_ids if i]
    if os.getenv("TEST"):
        return
    await homework_notifier(users_ids, serialized_data)


async def cron_notifier(text):
    users_ids = await sync_to_async(list)(
        DjangoUser.objects.filter(is_superuser=True).values(
            "server_user__telegram_id",
        ),
    )
    users_ids = [
        int(i["server_user__telegram_id"])
        for i in users_ids
        if i["server_user__telegram_id"]
    ]
    if os.getenv("TEST"):
        return
    await custom_notification(users_ids, text, False)
