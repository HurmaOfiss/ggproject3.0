from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID
from database import get_all_bookings, get_all_users
from keyboards import admin_panel_keyboard

async def admin_panel_logic(source):
    if isinstance(source, types.Message):
        await source.answer("⚙️ Админ-панель:", reply_markup=admin_panel_keyboard())
    else:
        await source.message.edit_text("⚙️ Админ-панель:", reply_markup=admin_panel_keyboard())
        await source.answer()

async def admin_bookings_logic(source):
    bookings = get_all_bookings()
    if not bookings:
        text = "📭 Нет ни одного бронирования."
    else:
        text = "📋 Все бронирования:\n\n"
        for booking_id, full_name, username, comp_num, start_date, start_time, end_date, end_time in bookings:
            user_info = f"{full_name} (@{username})" if username else full_name
            text += f"• {start_date} {start_time} – {end_date} {end_time} — ПК #{comp_num} — {user_info}\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    if isinstance(source, types.Message):
        await source.answer(text, reply_markup=keyboard)
    else:
        await source.message.edit_text(text, reply_markup=keyboard)
        await source.answer()

async def admin_users_logic(source):
    users = get_all_users()
    if not users:
        text = "📭 Нет зарегистрированных пользователей."
    else:
        text = "👥 Список пользователей:\n\n"
        for i, (user_id, nickname, full_name, username, phone, registered_at) in enumerate(users, 1):
            text += f"{i}. {full_name} (@{username if username else 'не указан'})\n"
            text += f"   • Никнейм: {nickname}\n"
            text += f"   • Телефон: {phone}\n"
            text += f"   • Зарегистрирован: {registered_at}\n\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    if isinstance(source, types.Message):
        await source.answer(text, reply_markup=keyboard)
    else:
        await source.message.edit_text(text, reply_markup=keyboard)
        await source.answer()