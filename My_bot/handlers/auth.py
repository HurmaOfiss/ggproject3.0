import sqlite3
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_ID
from database import register_user, login_user, is_authorized, get_db_connection
from utils import hash_password
from states import RegisterState, LoginState
from keyboards import reply_keyboard, unauth_reply_keyboard

async def register_start(message: types.Message, state: FSMContext):
    if is_authorized(message.from_user.id):
        await message.answer("Вы уже авторизованы.", reply_markup=reply_keyboard(message.from_user.id, ADMIN_ID))
        return
    await state.set_state(RegisterState.nickname)
    await message.answer("Введите ваш уникальный никнейм (латиница, цифры, _):")

async def register_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()
    if not nickname or len(nickname) > 30:
        await message.answer("Никнейм должен быть 1–30 символов. Попробуйте снова:")
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE nickname = ?", (nickname,))
    if cursor.fetchone():
        conn.close()
        await message.answer("Такой никнейм уже занят. Выберите другой:")
        return
    conn.close()
    await state.update_data(nickname=nickname)
    await state.set_state(RegisterState.name)
    await message.answer("Введите ваше имя:")

async def register_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Имя не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(name=name)
    await state.set_state(RegisterState.phone)
    await message.answer("Введите номер телефона, например (+79534943942):")

async def register_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not phone:
        await message.answer("Номер телефона не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await state.set_state(RegisterState.password)
    await message.answer("Придумайте пароль (минимум 4 символа):")

async def register_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    if len(password) < 4:
        await message.answer("Пароль должен быть не менее 4 символов. Попробуйте снова:")
        return
    data = await state.get_data()
    nickname = data["nickname"]
    name = data["name"]
    phone = data["phone"]
    user = message.from_user
    password_hash = hash_password(password)
    success = register_user(user.id, nickname, name, phone, password_hash, user.username, user.full_name)
    if success:
        await state.clear()
        await message.answer(
            "✅ Регистрация успешно завершена! Теперь вы можете пользоваться ботом.",
            reply_markup=reply_keyboard(user.id, ADMIN_ID)
        )
    else:
        await message.answer("❌ Ошибка регистрации. Возможно, никнейм уже существует. Начните заново /start")

async def login_start(message: types.Message, state: FSMContext):
    if is_authorized(message.from_user.id):
        await message.answer("Вы уже авторизованы.", reply_markup=reply_keyboard(message.from_user.id, ADMIN_ID))
        return
    await state.set_state(LoginState.nickname)
    await message.answer("Введите ваш никнейм:")

async def login_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()
    if not nickname:
        await message.answer("Никнейм не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(nickname=nickname)
    await state.set_state(LoginState.password)
    await message.answer("Введите пароль:")

async def login_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    nickname = data["nickname"]
    user = message.from_user
    password_hash = hash_password(password)
    success = login_user(user.id, nickname, password_hash)
    if success:
        await state.clear()
        await message.answer(
            f"✅ Вход выполнен! Добро пожаловать, {nickname}.",
            reply_markup=reply_keyboard(user.id, ADMIN_ID)
        )
    else:
        await message.answer("❌ Неверный никнейм или пароль. Попробуйте снова /start")