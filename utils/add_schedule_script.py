import os

import dotenv
import requests

dotenv.load_dotenv()

SUBJECTS_LIST = [
    "rus",
    "math",
    "lit",
    "okr",
    "eng",
    "ger",
    "geog",
    "hist",
    "soc",
    "law",
    "nat",
    "bio",
    "alg",
    "stat",
    "eco",
    "geom",
    "ast",
    "phys",
    "chem",
    "proj",
    "ikt",
    "izo",
    "mus",
    "tech",
    "obg",
    "ork",
    "odn",
    "info",
    "class",
    "phys-c",
]

DOMAIN = os.getenv("DOMAIN")

DAYS_IN_WEEK = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
}


def get_argument(help_text, condition, error, integer):
    boolean = True
    argument = ""
    while boolean:
        try:
            if integer:
                argument = int(input(help_text))
            else:
                argument = input(help_text)
        except ValueError:
            pass
        if argument in condition:
            boolean = False
        else:
            print(error)
    return argument


def fill_one_day():
    subjects = []
    number_of_lessons = int(input("Введите количество уроков: "))
    print(
        "Внимание! Вводите аббревиации уроков. Если урок есть у двух групп"
        " - пишите название предмета без цифры в конце",
    )
    for i in range(1, number_of_lessons + 1):
        subject_bool = True
        while subject_bool:
            subject = input(f"Введите урок под номером {i}: ")
            if subject not in SUBJECTS_LIST:
                print("Error: bad subject")
            else:
                subjects.append((i, subject))
                subject_bool = False
    return subjects


def set_one_day():
    weekday = get_argument(
        "Введите номер дня недели: ",
        [1, 2, 3, 4, 5, 6],
        "Ошибка: 1 <= weekday <= 6",
        True,
    )
    schedule = fill_one_day()
    print("\nвведенное расписание: ")
    print(f"{DAYS_IN_WEEK[weekday]}: ")
    for lesson in schedule:
        print(f"Урок №{lesson[0]}: {lesson[1]}")
    accept = int(input("Подтвердить? 1/0: ")) == 1
    if accept:
        for lesson in schedule:
            if lesson[1] in ["eng", "ger", "ikt"]:
                request_group = group
                subject = lesson[1] + str(group)
            else:
                request_group = 0
                subject = lesson[1]
            response = requests.post(
                DOMAIN + "/api/v1/add_schedule/",
                json={
                    "api_key": os.getenv("API_KEY"),
                    "telegram_id": os.getenv("SUPERUSER_TG_ID"),
                    "grade": grade,
                    "letter": letter,
                    "group": request_group,
                    "weekday": weekday,
                    "lesson": lesson[0],
                    "subject": subject,
                },
            )
            if response.status_code == 200:
                print(f"{lesson[0]}: {response} ✓")
            else:
                print(f"{lesson[0]}: {response} ✗")
        print("Все запросы отправлены")
    else:
        print("Операция отменена")


grade = get_argument(
    "Введите класс: ",
    [4, 5, 6, 7, 8, 9, 10, 11],
    "Ошибка: 4 <= grade <= 11",
    True,
)
letter = get_argument(
    "Введите литеру: ",
    ["А", "Б", "В", "Г"],
    "Ошибка: letter in [А, Б, В, Г]",
    False,
)
group = get_argument(
    "Введите группу: ",
    [1, 2],
    "Ошибка: group in [1, 2]",
    True,
)
for_week = int(input("Добавить дз для каждого дня недели? 1/0: ")) == 1

if not for_week:
    set_one_day()
else:
    while True:
        set_one_day()
        print()
        continue_bool = int(input("Продолжить? 1/0: ")) == 1
        if not continue_bool:
            break
