from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    start = State()
    choose_class = State()
    choose_group = State()
    become_admin = State()


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


class AddHomeworkFast(StatesGroup):
    choose_subject = State()
    add_data = State()
    add_descriptions_images = State()
    message_id = State()


class AddHomeworkSlow(StatesGroup):
    choose_subject = State()
    add_descriptions_images = State()
    add_files = State()
    message_id = State()


class EditHomework(StatesGroup):
    start = State()
    edit_text = State()
