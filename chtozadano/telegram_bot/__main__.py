import asyncio
import logging
import os
import sys

from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import (
    setup_application,
    SimpleRequestHandler,
)
from aiohttp import web
import dotenv
from bot_instance import bot
from handlers import (
    account_handlers,
    help_handler,
    homework_handlers,
    menu_handlers,
    register_handlers,
    schedule_handlers,
)

dotenv.load_dotenv()

USE_WEBHOOK = os.getenv("USE_WEBHOOK").lower() == "true"
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBHOOK_SECRET = os.getenv("SECRET_KEY")
BASE_WEBHOOK_URL = os.getenv("DOMAIN_URL")

dp = Dispatcher()
dp.include_routers(
    help_handler.rp_help_router,
    register_handlers.rp_register_router,
    menu_handlers.rp_menu_router,
    schedule_handlers.rp_schedule_router,
    account_handlers.rp_account_router,
    homework_handlers.rp_homework_router,
)


async def on_startup() -> None:
    await bot.set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
    )


def run_webhook() -> None:
    dp.startup.register(on_startup)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


async def run_polling() -> None:
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if USE_WEBHOOK:
        run_webhook()
    else:
        asyncio.run(run_polling())
