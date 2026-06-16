from datetime import datetime, timedelta
import sqlite3
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID, NOTIFY_MINUTES
from database import (
    get_computers, is_computer_free, add_booking,
    get_user_bookings, cancel_booking, get_db_connection
)
from states import BookingState
from keyboards import inline_main_keyboard, reply_keyboard

async def booking_start_logic(source, state: FSMContext):
    await state.set_state(BookingState.choosing_start_date)
    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(7)]
    buttons = [[InlineKeyboardButton(text=d.strftime("%d.%m.%Y"), callback_data=f"startdate_{d.strftime('%Y-%m-%d')}")] for d in dates]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if isinstance(source, types.Message):
        await source.answer("📅 Выберите дату начала бронирования:", reply_markup=keyboard)
    else:
        await source.message.edit_text("📅 Выберите дату начала бронирования:", reply_markup=keyboard)
        await source.answer()

async def process_start_date(callback: types.CallbackQuery, state: FSMContext):
    date_str = callback.data.split("_")[1]
    await state.update_data(start_date=date_str)
    await state.set_state(BookingState.choosing_start_time)

    hours = list(range(0, 25))
    buttons = [[InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"starttime_{h:02d}:00")] for h in hours]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="booking_start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        f"🕒 Выберите время начала на {datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')}:",
        reply_markup=keyboard
    )
    await callback.answer()

async def process_start_time(callback: types.CallbackQuery, state: FSMContext):
    start_time = callback.data.split("_")[1]
    await state.update_data(start_time=start_time)
    await state.set_state(BookingState.choosing_end_date)

    # Показываем выбор даты окончания (до 7 дней от start_date)
    data = await state.get_data()
    start_date = data["start_date"]
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dates = [start_dt + timedelta(days=i) for i in range(8)]  # до 7 дней
    buttons = [[InlineKeyboardButton(text=d.strftime("%d.%m.%Y"), callback_data=f"enddate_{d.strftime('%Y-%m-%d')}")] for d in end_dates]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="booking_start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "📅 Выберите дату окончания бронирования (до 7 дней от начала):",
        reply_markup=keyboard
    )
    await callback.answer()

async def process_end_date(callback: types.CallbackQuery, state: FSMContext):
    end_date = callback.data.split("_")[1]
    await state.update_data(end_date=end_date)
    await state.set_state(BookingState.choosing_end_time)

    # Показываем выбор времени окончания (от 00:00 до 23:00)
    hours = list(range(0, 24))
    buttons = [[InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"endtime_{h:02d}:00")] for h in hours]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="booking_start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        f"🕒 Выберите время окончания на {datetime.strptime(end_date, '%Y-%m-%d').strftime('%d.%m.%Y')}:",
        reply_markup=keyboard
    )
    await callback.answer()

async def process_end_time(callback: types.CallbackQuery, state: FSMContext):
    end_time = callback.data.split("_")[1]
    data = await state.get_data()
    start_date = data["start_date"]
    start_time = data["start_time"]
    end_date = data["end_date"]

    # Проверяем, что конечная дата+время позже начальных
    start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
    if end_dt <= start_dt:
        await callback.answer("Время окончания должно быть позже времени начала!", show_alert=True)
        return

    await state.update_data(end_time=end_time)
    await state.set_state(BookingState.choosing_computer)

    computers = get_computers()
    if not computers:
        await callback.message.edit_text("😞 Нет доступных компьютеров.")
        await state.clear()
        return

    free_computers = []
    for comp_id, comp_num, _ in computers:
        if is_computer_free(comp_id, start_date, start_time, end_date, end_time):
            free_computers.append((comp_id, comp_num))

    if not free_computers:
        await callback.message.edit_text(
            "😞 На выбранное время нет свободных компьютеров.\nПопробуйте выбрать другую дату или время.",
            reply_markup=inline_main_keyboard(callback.from_user.id, ADMIN_ID)
        )
        await state.clear()
        await callback.answer()
        return

    buttons = [[InlineKeyboardButton(text=f"Компьютер #{comp_num}", callback_data=f"comp_{comp_id}")] for comp_id, comp_num in free_computers]
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="booking_start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        f"🖥️ Выберите свободный компьютер\n"
        f"📅 {start_date} {start_time} – {end_date} {end_time}:",
        reply_markup=keyboard
    )
    await callback.answer()

async def process_computer(callback: types.CallbackQuery, state: FSMContext):
    comp_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    start_date = data["start_date"]
    start_time = data["start_time"]
    end_date = data["end_date"]
    end_time = data["end_time"]
    user_id = callback.from_user.id

    if not is_computer_free(comp_id, start_date, start_time, end_date, end_time):
        await callback.message.edit_text(
            "😞 К сожалению, этот компьютер уже забронирован. Пожалуйста, выберите другой.",
            reply_markup=inline_main_keyboard(user_id, ADMIN_ID)
        )
        await state.clear()
        await callback.answer()
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM computers WHERE id = ?", (comp_id,))
    comp_num = cursor.fetchone()[0]
    conn.close()

    success = add_booking(user_id, comp_id, start_date, start_time, end_date, end_time)
    if success:
        await callback.message.edit_text(
            f"✅ Бронирование успешно создано!\n\n"
            f"📅 {start_date} {start_time} – {end_date} {end_time}\n"
            f"🖥️ Компьютер: #{comp_num}\n\n"
            f"Ждем вас в Godje Club!",
            reply_markup=inline_main_keyboard(user_id, ADMIN_ID)
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось создать бронирование. Попробуйте позже.",
            reply_markup=inline_main_keyboard(user_id, ADMIN_ID)
        )
    await state.clear()
    await callback.answer()
async def show_my_bookings_logic(source):
    user_id = source.from_user.id
    bookings = get_user_bookings(user_id)
    if not bookings:
        text = "📭 У вас пока нет активных бронирований."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]])
    else:
        text = "📋 **Ваши бронирования:**\n\n"
        for booking_id, comp_num, start_date, start_time, end_date, end_time in bookings:
            text += f"• {start_date} {start_time} – {end_date} {end_time} — Компьютер #{comp_num}\n"
        buttons = [[InlineKeyboardButton(
            text=f"❌ Отменить {start_date} {start_time}–{end_time} (ПК #{comp_num})",
            callback_data=f"cancel_{booking_id}"
        )] for booking_id, comp_num, start_date, start_time, end_date, end_time in bookings]
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    if isinstance(source, types.Message):
        await source.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await source.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await source.answer()

async def cancel_booking_callback(callback: types.CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    success = cancel_booking(booking_id)
    if success:
        await callback.answer("Бронирование отменено.")
        await show_my_bookings_logic(callback)
    else:
        await callback.answer("Не удалось отменить бронирование.", show_alert=True)