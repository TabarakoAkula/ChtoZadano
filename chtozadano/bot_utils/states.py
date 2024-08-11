from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    start = State()
    choose_class = State()
    choose_group = State()


class Schedule(StatesGroup):
    start = State()
    week_schedule = State()
    tomorrow_schedule = State()
