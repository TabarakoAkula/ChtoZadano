import os
import random

import dotenv
import requests
from telegram.ext import Filters, MessageHandler, Updater

dotenv.load_dotenv()

DOMEN_URL = "http://web:8000/"


def handle_message(update, context):
    text = update.message.text.lower()
    if text == "код":
        user_id = update.message.chat_id
        user_name = update.message.from_user.first_name
        confirmation_code = random.randint(100000, 999999)
        update.message.reply_text(
            f"""Введите на сайте этот код ||{confirmation_code}||""",
        )
        requests.post(
            DOMEN_URL + "api/v1/code_confirmation/",
            data={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": user_id,
                "confirmation_code": confirmation_code,
                "name": user_name,
            },
        )
    elif text == "дз":
        user_id = update.message.chat_id
        homework = requests.get(
            DOMEN_URL + "api/v1/get_last_homework/",
            data={"api_key": os.getenv("API_KEY"), "telegram_id": user_id},
        )
        update.message.reply_text(
            f"""{homework.json()}""",
        )
    for subject in [
        "Русский язык",
        "Математика",
        "Литература",
        "Окружающий мир",
        "Английский",
        "Немецкий",
        "Немецкий",
        "География",
        "История",
        "Обществознание",
        "Право",
        "Естествознание",
        "Биология",
        "Алгебра",
        "Вероятность и статистика",
        "Экономика",
        "Геометрия",
        "Астрономия",
        "Физика",
        "Химия",
        "Индивидуальный проект" "Информатика" "ИЗО",
        "Музыка",
        "Технология",
        "ОБЖ",
        "ОРКСЭ",
        "ОДНКНР",
        "ИНФОРМАЦИЯ",
    ]:
        if subject.lower() in text.lower():
            user_id = update.message.chat_id
            homework = requests.get(
                DOMEN_URL + "api/v1/get_homework_for_subject/",
                data={
                    "api_key": os.getenv("API_KEY"),
                    "telegram_id": user_id,
                    "subject": subject,
                },
            )
            update.message.reply_text(
                f"""{homework.json()}""",
            )


def main():
    token = os.getenv("BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message),
    )
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
