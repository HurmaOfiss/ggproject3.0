from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

def unauth_reply_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🔑 Вход")],
        [KeyboardButton(text="📝 Регистрация")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def reply_keyboard(user_id: int, admin_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🖥️ Забронировать компьютер")],
        [KeyboardButton(text="📋 Мои бронирования")],
        [KeyboardButton(text="💰 Тарифы")],
        [KeyboardButton(text="ℹ️ О клубе")]
    ]
    if user_id == admin_id:
        buttons.append([KeyboardButton(text="⚙️ Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def inline_main_keyboard(user_id: int, admin_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🖥️ Забронировать компьютер", callback_data="booking_start")],
        [InlineKeyboardButton(text="📋 Мои бронирования", callback_data="my_bookings")],
        [InlineKeyboardButton(text="💰 Тарифы", callback_data="tariffs")],
        [InlineKeyboardButton(text="ℹ️ О клубе", callback_data="info")]
    ]
    if user_id == admin_id:
        buttons.append([InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📋 Просмотр броней", callback_data="admin_bookings")],
        [InlineKeyboardButton(text="👥 Просмотр пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def info_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🎧 Оборудование", callback_data="equipment")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tariffs_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])

def equipment_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к информации", callback_data="info")]
    ])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking_flow")]
    ])