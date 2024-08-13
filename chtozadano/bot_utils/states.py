from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    start = State()
    choose_class = State()
    choose_group = State()


class Schedule(StatesGroup):
    start = State()
    week_schedule = State()
    tomorrow_schedule = State()


class Account(StatesGroup):
    start = State()
    change_contacts = State()
    become_admin = State()
    settings = State()


class ChangeContacts(StatesGroup):
    first_name = State()
    last_name = State()


class Homework(StatesGroup):
    start = State()
    subject = State()
    find = State()
