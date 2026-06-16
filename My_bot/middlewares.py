from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database import is_authorized
from keyboards import unauth_reply_keyboard

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        if event.text in ("🔑 Вход", "📝 Регистрация"):
            return await handler(event, data)

        state = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state and (current_state.startswith("RegisterState:") or current_state.startswith("LoginState:")):
                return await handler(event, data)

        if not is_authorized(user_id):
            await event.answer(
                "🔒 Для использования бота необходимо войти или зарегистрироваться.",
                reply_markup=unauth_reply_keyboard()
            )
            return

        return await handler(event, data)

class CallbackAuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if not is_authorized(user_id):
            state = data.get("state")
            if state:
                current_state = await state.get_state()
                if current_state and (current_state.startswith("RegisterState:") or current_state.startswith("LoginState:")):
                    return await handler(event, data)
            await event.answer("🔒 Сначала войдите или зарегистрируйтесь.", show_alert=True)
            return
        return await handler(event, data)