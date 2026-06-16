import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter

from config import BOT_TOKEN, NOTIFY_MINUTES
from database import init_db, get_bookings_to_notify, mark_notified
from middlewares import AuthMiddleware, CallbackAuthMiddleware
from states import RegisterState, LoginState, BookingState, AdminState
from handlers import (
    cmd_start,
    register_start, register_nickname, register_name, register_phone, register_password,
    login_start, login_nickname, login_password,
    booking_start_logic, process_start_date, process_start_time, process_end_date, process_end_time, process_computer,
    show_my_bookings_logic, cancel_booking_callback,
    tariffs_logic, info_logic, equipment_logic,
    admin_panel_logic, admin_bookings_logic, admin_users_logic,
    admin_computers_logic, admin_add_computer_callback, admin_add_computer_message,
    admin_delete_computer_callback, admin_delete_computer_message,
    admin_toggle_computer_callback, admin_toggle_computer_message,
    admin_logs_logic,
    back_to_main_callback, cancel_flow_callback
)

logging.basicConfig(level=logging.INFO)

async def notify_task(bot: Bot):
    while True:
        try:
            bookings = get_bookings_to_notify(NOTIFY_MINUTES)
            for booking_id, user_id, start_date, start_time, end_date, end_time, comp_num in bookings:
                try:
                    await bot.send_message(
                        user_id,
                        f"⏰ Напоминание! Ваше бронирование начнётся через {NOTIFY_MINUTES} минут.\n"
                        f"📅 {start_date} {start_time} – {end_date} {end_time}\n"
                        f"🖥️ Компьютер #{comp_num}\n\n"
                        f"Ждём вас в Godje Club!"
                    )
                    mark_notified(booking_id)
                except Exception as e:
                    logging.error(f"Ошибка отправки уведомления для брони {booking_id}: {e}")
        except Exception as e:
            logging.error(f"Ошибка в notify_task: {e}")
        await asyncio.sleep(60)

async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(CallbackAuthMiddleware())

    dp.message.register(cmd_start, Command("start"))

    dp.message.register(register_start, lambda msg: msg.text == "📝 Регистрация")
    dp.message.register(register_nickname, RegisterState.nickname)
    dp.message.register(register_name, RegisterState.name)
    dp.message.register(register_phone, RegisterState.phone)
    dp.message.register(register_password, RegisterState.password)

    dp.message.register(login_start, lambda msg: msg.text == "🔑 Вход")
    dp.message.register(login_nickname, LoginState.nickname)
    dp.message.register(login_password, LoginState.password)

    dp.message.register(booking_start_logic, lambda msg: msg.text == "🖥️ Забронировать компьютер")
    dp.message.register(show_my_bookings_logic, lambda msg: msg.text == "📋 Мои бронирования")
    dp.message.register(tariffs_logic, lambda msg: msg.text == "💰 Тарифы")
    dp.message.register(info_logic, lambda msg: msg.text == "ℹ️ О клубе")
    dp.message.register(admin_panel_logic, lambda msg: msg.text == "⚙️ Админ-панель")

    dp.callback_query.register(process_start_date, BookingState.choosing_start_date, lambda c: c.data.startswith("startdate_"))
    dp.callback_query.register(process_start_time, BookingState.choosing_start_time, lambda c: c.data.startswith("starttime_"))
    dp.callback_query.register(process_end_date, BookingState.choosing_end_date, lambda c: c.data.startswith("enddate_"))
    dp.callback_query.register(process_end_time, BookingState.choosing_end_time, lambda c: c.data.startswith("endtime_"))
    dp.callback_query.register(process_computer, BookingState.choosing_computer, lambda c: c.data.startswith("comp_"))

    dp.callback_query.register(booking_start_logic, lambda c: c.data == "booking_start")
    dp.callback_query.register(show_my_bookings_logic, lambda c: c.data == "my_bookings")
    dp.callback_query.register(tariffs_logic, lambda c: c.data == "tariffs")
    dp.callback_query.register(info_logic, lambda c: c.data == "info")
    dp.callback_query.register(equipment_logic, lambda c: c.data == "equipment")
    dp.callback_query.register(cancel_booking_callback, lambda c: c.data.startswith("cancel_"))
    dp.callback_query.register(back_to_main_callback, lambda c: c.data == "back_to_main")
    dp.callback_query.register(cancel_flow_callback, lambda c: c.data == "cancel_booking_flow")

    dp.callback_query.register(admin_panel_logic, lambda c: c.data == "admin_panel")
    dp.callback_query.register(admin_bookings_logic, lambda c: c.data == "admin_bookings")
    dp.callback_query.register(admin_users_logic, lambda c: c.data == "admin_users")
    dp.callback_query.register(admin_computers_logic, lambda c: c.data == "admin_computers")
    dp.callback_query.register(admin_add_computer_callback, lambda c: c.data == "admin_add_computer")
    dp.callback_query.register(admin_delete_computer_callback, lambda c: c.data == "admin_delete_computer")
    dp.callback_query.register(admin_toggle_computer_callback, lambda c: c.data == "admin_toggle_computer")
    dp.callback_query.register(admin_logs_logic, lambda c: c.data == "admin_logs")

    dp.message.register(admin_add_computer_message, StateFilter(AdminState.add_computer))
    dp.message.register(admin_delete_computer_message, StateFilter(AdminState.delete_computer))
    dp.message.register(admin_toggle_computer_message, StateFilter(AdminState.toggle_computer))

    @dp.callback_query()
    async def unknown_callback(callback):
        await callback.answer("Неизвестная команда.", show_alert=False)

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(notify_task(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())