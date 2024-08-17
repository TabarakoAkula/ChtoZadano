from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


rp_help_router = Router()


@rp_help_router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        "/start - инициализировать бота\n"
        "/reset - сменить класс\n"
        "/menu - меню\n"
        "/code - код верификации\n"
        "/get_week_schedule - расписание на неделю\n"
        "/get_tomorrow_schedule - расписание на завтра\n"
        "/change_contacts - изменить имя или фамилию\n"
        "/become_admin - стать администратором\n"
        "/settings - настройки\n"
        "/tomorrow - посмотреть дз на завтра\n"
        "/subject - посмотреть дз по конкретному предмету\n"
        "/new - добавить домашнее задание\n"
        "/publish - опубликовать домашнее задание\n"
        "/stop - прекратить добавление домашнего задания\n"
        "/date - поиск домашки по дате\n",
    )


# /show_become_admin - просмотр заявок на администратора
# /add_mailing - добавить рассылку
