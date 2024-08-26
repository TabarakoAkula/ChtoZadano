import asyncio
import csv
import os

import aiohttp
import dotenv

dotenv.load_dotenv()

complete_tasks = 0


def get_csv_data(
    filename: str,
    delimiter: str = ";",
    encoding: str = "utf-8",
) -> dict:
    with open(filename, mode="r", encoding=encoding) as file:
        reader = csv.reader(file, delimiter=delimiter)
        file_headers = next(reader)
        schedule = {}
        for row in reader:
            last_weekday = None
            last_grade = None
            day_schedule = {}
            for index in range(len(file_headers)):
                row_header = file_headers[index]
                row_data = row[index]
                if row_header == "grade":
                    last_grade = row_data
                    if last_grade:
                        schedule[row_data] = {}
                else:
                    weekday, lesson = list(map(int, row_header.split("_")))
                    if last_weekday != weekday:
                        last_weekday = weekday
                        if last_weekday:
                            schedule[last_grade][last_weekday] = day_schedule
                        day_schedule = {}

                        schedule_len = len(day_schedule)
                        if row_data:
                            if len(row_data.split("/")) == 2:
                                day_schedule[
                                    schedule_len + 1
                                ] = row_data.strip().split("/")
                            else:
                                day_schedule[
                                    schedule_len + 1
                                ] = row_data.strip()
                    else:
                        schedule_len = len(day_schedule)
                        if row_data:
                            if len(row_data.split("/")) == 2:
                                day_schedule[
                                    schedule_len + 1
                                ] = row_data.strip().split("/")
                            else:
                                day_schedule[
                                    schedule_len + 1
                                ] = row_data.strip()
    return schedule


async def make_post_request(url: str, data: dict) -> None:
    global complete_tasks
    async with (aiohttp.ClientSession() as session):
        async with session.post(url, json=data) as response:
            response_status_code = response.status
            response_data = await response.json()
            if response_status_code != 200:
                print(
                    f"ERROR: status_code: {response_status_code}\n"
                    f"response_data: {response_data}\n",
                )
            complete_tasks += 1
            if (
                complete_tasks % 10 == 0
                and complete_tasks != tasks_number
                or complete_tasks == tasks_number
            ):
                text = f"\rComplete: {complete_tasks}/{tasks_number}"
                lost = (tasks_number - complete_tasks) // 10
                progress_bar = (complete_tasks // 10) * "█" + lost * "/"
                print(f"{text} [{progress_bar}]", flush=True, end="")
            await asyncio.sleep(0.25)
            return


if __name__ == "__main__":
    DOMAIN_URL = os.getenv("DOMAIN_URL")
    TELEGRAM_ID = os.getenv("SUPERUSER_ID")
    API_KEY = os.getenv("API_KEY")

    FILENAME = "timetable.csv"
    DELIMITER = ";"
    ENCODING = "utf-8"

    url = DOMAIN_URL + "/api/v1/add_schedule/"
    schedule = get_csv_data(
        filename=FILENAME,
        delimiter=DELIMITER,
        encoding=ENCODING,
    )
    tasks = []
    tasks_number = 0
    short_tasks = []
    for grade_letter in schedule:
        grade = grade_letter[:-1]
        letter = grade_letter[-1].upper()

        for day in schedule[grade_letter]:
            for lesson in schedule[grade_letter][day]:
                lesson_subject = schedule[grade_letter][day][lesson]
                if isinstance(lesson_subject, list):
                    for i in range(2):
                        request_data = {
                            "api_key": API_KEY,
                            "telegram_id": TELEGRAM_ID,
                            "grade": grade,
                            "letter": letter,
                            "group": i + 1,
                            "weekday": day,
                            "lesson": lesson,
                            "subject": lesson_subject[i],
                        }
                        short_tasks.append(
                            make_post_request(url, request_data),
                        )
                        tasks_number += 1
                else:
                    request_data = {
                        "api_key": API_KEY,
                        "telegram_id": TELEGRAM_ID,
                        "grade": grade,
                        "letter": letter,
                        "group": 0,
                        "weekday": day,
                        "lesson": lesson,
                        "subject": lesson_subject,
                    }
                    short_tasks.append(make_post_request(url, request_data))
                    tasks_number += 1
            if len(short_tasks) % 5 == 0:
                tasks.append(short_tasks)
                short_tasks = []
    loop = asyncio.get_event_loop()
    try:
        for tasks_group in tasks:
            loop.run_until_complete(asyncio.gather(*tasks_group))
    except aiohttp.client.ClientConnectorError:
        print("\nERROR: Can not connect to server :\\")
    else:
        text = f"Complete: {complete_tasks}/{complete_tasks}"
        progress_bar = complete_tasks // 10 * "█"
        print("\r" + text, "[" + progress_bar + "]  ")
        print("SUCCESS: Successfully add schedule")
