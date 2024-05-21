from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    gender = State()
    interested = State()
    age = State()
    username = State()
    description = State()
    image = State()
    city = State()


class ChangeUser(StatesGroup):
    clause = State()
    username = State()
    description = State()
    image = State()
