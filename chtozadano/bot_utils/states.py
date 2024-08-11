from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    start = State()
    choose_class = State()
    choose_group = State()
    reset = State()
