import os
import logging
from aiogram import types, Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_ID, TARIFFS_PHOTO_PATH, EQUIPMENT_PHOTOS
from keyboards import (
    reply_keyboard, unauth_reply_keyboard, inline_main_keyboard,
    info_keyboard, tariffs_back_keyboard, equipment_back_keyboard
)
from database import is_authorized

async def cmd_start(message: types.Message, state: FSMContext):
    user = message.from_user
    if is_authorized(user.id):
        await message.answer(
            f"С возвращением, {user.full_name}!",
            reply_markup=reply_keyboard(user.id, ADMIN_ID)
        )
        return
    await message.answer(
        f"Добро пожаловать, {user.full_name}!\n\n"
        "Для использования бота необходимо войти или зарегистрироваться.",
        reply_markup=unauth_reply_keyboard()
    )

async def tariffs_logic(source):
    caption = (
        "💰 **Тарифы**\n\n"
        "Для постоянных клиентов действуют накопительные скидки!"
    )
    try:
        photo = FSInputFile(TARIFFS_PHOTO_PATH)
        if isinstance(source, types.Message):
            await source.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=tariffs_back_keyboard())
        else:
            await source.message.delete()
            await source.message.answer_photo(photo, caption=caption, parse_mode="Markdown", reply_markup=tariffs_back_keyboard())
            await source.answer()
    except Exception as e:
        logging.error(f"Ошибка отправки фото тарифов: {e}")
        if isinstance(source, types.Message):
            await source.answer(caption, parse_mode="Markdown")
        else:
            await source.message.edit_text(caption, parse_mode="Markdown", reply_markup=tariffs_back_keyboard())
            await source.answer()

async def info_logic(source):
    text = (
        "🏆 Godje Club — современный компьютерный клуб с мощными ПК и уютной атмосферой.\n\n"
        "📍 Адрес: ул. Примерная, д. 1\n"
        "🕒 Режим работы: круглосуточно\n"
        "📞 Контактный телефон: +7 (999) 123-45-67\n"
        "🌐 Сайт: godjeclub.ru"
    )
    if isinstance(source, types.Message):
        await source.answer(text, reply_markup=info_keyboard())
    else:
        await source.message.edit_text(text, reply_markup=info_keyboard())
        await source.answer()

async def equipment_logic(source):
    caption = "🎧 Наше оборудование: современные гарнитуры, мощные ПК."
    media_group = []
    for i, path in enumerate(EQUIPMENT_PHOTOS):
        if not os.path.exists(path):
            continue
        if i == 0:
            media_group.append(InputMediaPhoto(media=FSInputFile(path), caption=caption))
        else:
            media_group.append(InputMediaPhoto(media=FSInputFile(path)))
    if not media_group:
        await source.answer("Фото оборудования временно недоступны.", reply_markup=equipment_back_keyboard())
        return
    if isinstance(source, types.Message):
        await source.answer_media_group(media=media_group)
        await source.answer("👇", reply_markup=equipment_back_keyboard())
    else:
        await source.message.delete()
        await source.message.answer_media_group(media=media_group)
        await source.message.answer("👇", reply_markup=equipment_back_keyboard())
        await source.answer()

async def back_to_main_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=reply_keyboard(callback.from_user.id, ADMIN_ID)
    )
    await callback.answer()

async def cancel_flow_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Действие отменено.",
        reply_markup=reply_keyboard(callback.from_user.id, ADMIN_ID)
    )
    await callback.answer()