import asyncio
import datetime
import json
import random

from celery import shared_task
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.files.storage import default_storage
import django.db.models
from django.db.models import Max, Q, Subquery
from django.http import request as type_request
from django.shortcuts import redirect
import dotenv

from homework.api.serializers import HomeworkSerializer
import homework.models
from homework.notifier import custom_notification, homework_notifier
from users.api.serializers import UserNotificationsSerializer
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
            for subject in user_subjects:
                if isinstance(json_subject_data[subject], list):
                    response.append(json_subject_data[subject][0].lower())
                else:
                    response.append(json_subject_data[subject].lower())
    return response


def get_user_group_subjects(grade: int, letter: str) -> list:
    grades_subjects_url = staticfiles_storage.url("json/grades_subjects.json")
    with open(str(BASE_DIR) + grades_subjects_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        return json_data[str(grade)][letter]["group_subject_codes"]


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


def get_group_from_teacher(teacher_name: str, grade: int, letter: str) -> int:
    eng_teachers_url = staticfiles_storage.url("json/eng_teachers.json")
    with open(str(BASE_DIR) + eng_teachers_url, encoding="utf-8") as data:
        json_data = json.loads(data.read())
        try:
            return json_data[teacher_name]["grades"][f"{grade}{letter}"]
        except KeyError:
            return 0


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
                "Сначала необходимо выбрать в каком ты классе",
            )
            return "Error", redirect("homework:choose_grad_let")
        grade = data["grade"]
        letter = data["letter"]
        group = data["group"]
        if not grade or not letter:
            messages.error(
                request,
                "Сначала необходимо выбрать в каком ты классе",
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


def add_notification_management(
    homework_data,
    user_data,
    use_groups_data: bool = False,
) -> None:
    if settings.USE_CELERY:
        celery_add_notification.delay(
            HomeworkSerializer(homework_data).data,
            UserNotificationsSerializer(user_data).data,
            use_groups_data,
        )
    else:
        add_notification(
            HomeworkSerializer(homework_data).data,
            user_data,
            use_groups_data,
        )


@shared_task()
def celery_add_notification(
    model_object,
    user,
    use_groups: bool = False,
) -> None:
    return add_notification(model_object, user, use_groups, True)


def add_notification(
    model_object,
    user,
    use_groups: bool = False,
    use_celery: bool = False,
) -> None:
    if use_celery:
        user_instance = users.models.User.objects.get(
            telegram_id=user["telegram_id"],
        )
        serializer = UserNotificationsSerializer(
            instance=user_instance,
            data=user,
        )
        if serializer.is_valid():
            user = serializer.save()
        else:
            return
    if use_groups:
        users_ids = users.models.User.objects.filter(
            grade=user.grade,
            letter=user.letter,
            group=user.group,
            chat_mode=True,
        ).values("telegram_id")
    else:
        users_ids = users.models.User.objects.filter(
            grade=user.grade,
            letter=user.letter,
            chat_mode=True,
        ).values("telegram_id")
    users_ids = [i["telegram_id"] for i in users_ids]
    users_ids = [i for i in users_ids if i]
    if settings.TEST:
        return
    asyncio.run(homework_notifier(users_ids, model_object))


def cron_notification_management(text):
    if settings.USE_CELERY:
        celery_cron_notification.delay(text)
    else:
        cron_notifier(text)


@shared_task()
def celery_cron_notification(text):
    return cron_notifier(text)


def cron_notifier(text: str) -> None:
    users_ids = DjangoUser.objects.filter(is_superuser=True).values(
        "server_user__telegram_id",
    )
    users_ids = [
        int(i["server_user__telegram_id"])
        for i in users_ids
        if i["server_user__telegram_id"]
    ]
    if settings.TEST:
        return
    asyncio.run(custom_notification(users_ids, text, False))


def delete_old_homework_management():
    if settings.USE_CELERY:
        celery_delete_old_homework.delay()
    else:
        delete_old_homework()


@shared_task()
def celery_delete_old_homework():
    return delete_old_homework()


def get_all_grades() -> list[tuple[int, str]]:
    grades_subjects_url = staticfiles_storage.url("json/grades_subjects.json")
    grades_list = []
    with open(
        str(BASE_DIR) + grades_subjects_url,
        encoding="utf-8",
    ) as data:
        json_data = json.loads(data.read())
        for grade in json_data:
            for letter in json_data[grade].keys():
                grades_list.append((int(grade), letter))
        return grades_list


def delete_old_homework() -> None:
    today = datetime.datetime.today().date()
    two_weeks_ago = today - datetime.timedelta(days=14)
    all_ids_for_exclude = []
    for grade_letter in get_all_grades():
        latest_homework = (
            homework.models.Homework.objects.filter(
                grade=grade_letter[0],
                letter=grade_letter[1],
            )
            .values("subject")
            .annotate(latest_created_at=Max("created_at"))
        )
        latest_homework_ids = homework.models.Homework.objects.filter(
            grade=grade_letter[0],
            letter=grade_letter[1],
            created_at__in=Subquery(
                latest_homework.values("latest_created_at"),
            ),
            subject__in=latest_homework.values("subject"),
        ).values("id")
        for one_id in latest_homework_ids:
            all_ids_for_exclude.append(one_id["id"])
    todo_objects = homework.models.Todo.objects.filter(
        created_at__lt=two_weeks_ago,
    ).exclude(homework_todo__id__in=all_ids_for_exclude)
    hw_objects = homework.models.Homework.objects.filter(
        created_at__lt=two_weeks_ago,
    ).exclude(id__in=all_ids_for_exclude)
    response_message = (
        f"Cleaner🗑️: Успешно удалено:\n"
        f"· {todo_objects.count()} Todo записей\n"
        f"· {hw_objects.count()} Homework записей"
    )
    todo_objects.delete()
    hw_objects.delete()
    cron_notification_management(response_message)
    return


def redis_delete_data(
    homework_data: bool = True,
    grade: int = 0,
    letter: str = "",
    group: int = 0,
    schedule: bool = False,
) -> None:
    use_redis = False
    redis_client = None
    cache_backend = settings.CACHES["default"]["BACKEND"]
    if cache_backend == "django_redis.cache.RedisCache":
        use_redis = True
        redis_client = cache.client.get_client()
    cache_keys = []
    specific_keys = []
    if homework_data:
        cache_keys += [
            f"homework_page_data_{grade}_{letter}_{group}",
        ]
        specific_keys += [
            f"weekday_page_data_{grade}_{letter}_{group}_*",
            f"all_homework_date_{grade}_{letter}_{group}_*",
            f"all_homework_data_{grade}_{letter}_*",
        ]
    if not homework_data and not schedule:
        cache_keys += [
            f"homework_page_info_class_{grade}_{letter}",
            "homework_page_info_admin",
            "homework_page_info_school",
        ]
    if not homework_data and schedule:
        cache_keys += [
            f"schedule_{grade}_{letter}_{group}",
            f"tomorrow_schedule_{grade}_{letter}_{group}",
        ]
    if use_redis:
        for key_pattern in specific_keys:
            keys = redis_client.scan_iter(key_pattern)
            cache_keys += keys
    cache.delete_many(cache_keys)
    return
