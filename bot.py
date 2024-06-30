import os
import random

import dotenv
import requests
from telegram.ext import Filters, MessageHandler, Updater


dotenv.load_dotenv()


def handle_message(update, context):
    text = update.message.text.lower()
    if text in ["код", "code", "kod", "rjl"]:
        user_id = update.message.chat_id
        user_name = update.message.from_user.first_name
        confirmation_code = random.randint(100000, 999999)
        update.message.reply_text(
            f"""Введите на сайте этот код ||{confirmation_code}||""",
        )
        requests.post(
            "http://127.0.0.1:8000/api/v1/sign_in/",
            data={
                "api_key": os.getenv("API_KEY"),
                "telegram_id": user_id,
                "confirmation_code": confirmation_code,
                "name": user_name,
            },
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
