from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils import check_for_admin


rp_help_router = Router()


@rp_help_router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    text = [
        'Давай расскажу о доступных тебе командах "А что задано?"',
        "",
        "/tomorrow - посмотреть дз на завтра",
        "/get_week_schedule - посмотреть расписание на неделю",
        "/get_tomorrow_schedule - посмотреть расписание на завтра",
        "/code - сгенерировать код верификации для регистрации на сайте",
        "/change_contacts - изменить имя или фамилию",
        "/settings - изменить настройки",
        "/date - искать домашнее задание по дате",
        "/stop - прекратить добавление домашнего задания",
        "/reset - сменить класс",
    ]
    if await check_for_admin(message.chat.id) in ["admin", "superuser"]:
        text.extend(
            [
                "",
                "Команды для администраторов:",
                "/new - добавить домашнее задание",
                "/add_mailing - добавить информацию",
                "/show_become_admin - просмотр заявок на администратора",
            ]
        )
    else:
        text.append("/become_admin - стать администратором")

    await message.answer("\n".join(text))
