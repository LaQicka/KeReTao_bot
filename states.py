from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class UserState(StatesGroup):
    in_system = State()
    registration = State()
    

class AdminState(StatesGroup):
    normal = State()
    msg_wait = State()