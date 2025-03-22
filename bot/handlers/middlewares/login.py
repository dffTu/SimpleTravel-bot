import aiogram
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.fsm.context import FSMContext
from bot.globals import database
from bot.handlers.register import RegisterForm

class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Получаем состояние FSM
        state: FSMContext = data.get('state')
        current_state = await state.get_state() if state else None

        # Исключения когда регистрироваться не нужно
        if event.message and (event.message.text == "/start" or current_state in [
            RegisterForm.name_question.state,
            RegisterForm.phone_question.state,
            RegisterForm.email_question.state
        ]):
            return await handler(event, data)

        if 'user' not in data:
            user_id = None

            if event.message:
                user_id = event.message.from_user.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id

            user_info = database.get_user(user_id)
            if not user_info:
                if event.message:
                    await event.message.answer("Не удалось определить пользователя. Пожалуйста, зарегистрируйтесь.")
                elif event.callback_query:
                    await event.callback_query.answer("Не удалось определить пользователя. Пожалуйста, зарегистрируйтесь.")
                return
            data['user'] = user_info
        return await handler(event, data)
