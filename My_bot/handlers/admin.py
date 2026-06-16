from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID
from database import (
    get_all_bookings, get_all_users, get_computers,
    add_computer, delete_computer, toggle_computer_active,
    log_admin_action, get_admin_logs
)
from keyboards import admin_panel_keyboard
from states import AdminState

# ---- Старые функции ----

async def admin_panel_logic(source):
    if isinstance(source, types.Message):
        await source.answer("⚙️ Админ-панель:", reply_markup=admin_panel_keyboard())
        log_admin_action(source.from_user.id, "Открыл админ-панель", "через сообщение")
    else:
        await source.message.edit_text("⚙️ Админ-панель:", reply_markup=admin_panel_keyboard())
        await source.answer()
        log_admin_action(source.from_user.id, "Открыл админ-панель", "через callback")

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
    log_admin_action(source.from_user.id, "Просмотр всех броней")

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
    log_admin_action(source.from_user.id, "Просмотр списка пользователей")

# ---- Новые функции: управление компьютерами ----

async def admin_computers_logic(source):
    computers = get_computers(active_only=False)
    if not computers:
        text = "📭 Нет компьютеров."
    else:
        text = "🖥️ Список компьютеров:\n\n"
        for comp_id, number, is_active in computers:
            status = "✅ Активен" if is_active else "❌ Неактивен"
            text += f"• #{number} (ID {comp_id}) — {status}\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить компьютер", callback_data="admin_add_computer")],
        [InlineKeyboardButton(text="🗑 Удалить компьютер", callback_data="admin_delete_computer")],
        [InlineKeyboardButton(text="🔄 Переключить статус", callback_data="admin_toggle_computer")],
        [InlineKeyboardButton(text="📜 Логи админа", callback_data="admin_logs")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    if isinstance(source, types.Message):
        await source.answer(text, reply_markup=keyboard)
    else:
        await source.message.edit_text(text, reply_markup=keyboard)
        await source.answer()
    log_admin_action(source.from_user.id, "Просмотр списка компьютеров")

async def admin_add_computer_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.add_computer)
    await callback.message.edit_text("Введите номер нового компьютера (целое число):")
    await callback.answer()

async def admin_add_computer_message(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введите корректное целое число.")
        return
    number = int(message.text)
    success = add_computer(number)
    if success:
        await message.answer(f"✅ Компьютер #{number} добавлен.")
        log_admin_action(message.from_user.id, "Добавлен компьютер", f"номер {number}")
    else:
        await message.answer(f"❌ Не удалось добавить компьютер (возможно, номер уже существует).")
    await state.clear()
    await admin_computers_logic(message)

async def admin_delete_computer_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.delete_computer)
    await callback.message.edit_text("Введите ID компьютера для удаления (из списка выше):")
    await callback.answer()

async def admin_delete_computer_message(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введите корректный ID.")
        return
    comp_id = int(message.text)
    success = delete_computer(comp_id)
    if success:
        await message.answer(f"✅ Компьютер с ID {comp_id} удалён.")
        log_admin_action(message.from_user.id, "Удалён компьютер", f"ID {comp_id}")
    else:
        await message.answer(f"❌ Не удалось удалить компьютер (возможно, на него есть брони).")
    await state.clear()
    await admin_computers_logic(message)

async def admin_toggle_computer_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.toggle_computer)
    await callback.message.edit_text("Введите ID компьютера для переключения статуса (активен/неактивен):")
    await callback.answer()

async def admin_toggle_computer_message(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введите корректный ID.")
        return
    comp_id = int(message.text)
    success = toggle_computer_active(comp_id)
    if success:
        await message.answer(f"✅ Статус компьютера с ID {comp_id} изменён.")
        log_admin_action(message.from_user.id, "Переключён статус компьютера", f"ID {comp_id}")
    else:
        await message.answer(f"❌ Компьютер с ID {comp_id} не найден.")
    await state.clear()
    await admin_computers_logic(message)

# ---- Логи администратора ----

async def admin_logs_logic(source):
    logs = get_admin_logs(20)
    if not logs:
        text = "📭 Логов нет."
    else:
        text = "📋 Последние действия администратора:\n\n"
        for log_id, admin_id, action, details, created_at in logs:
            text += f"• {created_at}: {action}"
            if details:
                text += f" ({details})"
            text += "\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    if isinstance(source, types.Message):
        await source.answer(text, reply_markup=keyboard)
    else:
        await source.message.edit_text(text, reply_markup=keyboard)
        await source.answer()