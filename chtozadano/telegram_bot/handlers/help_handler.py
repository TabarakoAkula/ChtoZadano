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
    is_admin = await check_for_admin(message.chat.id)
    if is_admin == "admin":
        text.extend(
            [
                "",
                "Команды для администраторов:",
                "/new - добавить домашнее задание",
                "/info - опубликовать информацию для класса",
            ],
        )
    elif is_admin == "superuser":
        text.extend(
            [
                "",
                "Команды для администраторов:",
                "/new - добавить домашнее задание",
                "/info - опубликовать информацию для класса",
                "",
                "Команды для суперпользователей:",
                "/add_mailing - добавить информацию",
                "/show_become_admin - просмотр заявок на администратора",
            ],
        )
    elif not is_admin:
        await message.answer(
            "Для взаимодействия с ботом необходимо в нем зарегистрироваться."
            " Введи команду /start",
        )
    else:
        text.append("/become_admin - стать администратором")
    if is_admin:
        await message.answer("\n".join(text))
