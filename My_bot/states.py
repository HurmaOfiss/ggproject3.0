from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    nickname = State()
    name = State()
    phone = State()
    password = State()

class LoginState(StatesGroup):
    nickname = State()
    password = State()

class BookingState(StatesGroup):
    choosing_start_date = State()
    choosing_start_time = State()
    choosing_end_date = State()      # новое
    choosing_end_time = State()
    choosing_computer = State()

class AdminState(StatesGroup):
    add_computer = State()
    delete_computer = State()
    toggle_computer = State()