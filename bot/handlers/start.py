import asyncio
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.search import start_search_session
from bot.handlers.post import start_post_session
from bot.handlers.account import start_account_session
from bot.handlers.start_entry import start_entry

start_router = Router()



@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await start_entry(message, state)


# Обработчик для кнопки "Искать мероприятия"
@start_router.callback_query(lambda c: c.data and c.data == "start_search")
async def search_activities(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # Убираем индикатор загрузки
    await callback.message.delete_reply_markup()  # Убираем кнопки у сообщения
    await callback.message.answer(
        "Прекрасно! Давайте найдем для вас что-то интересное..."
    )
    await start_search_session(callback.message, state)


# Обработчик для кнопки "Разместить свое мероприятие"
@start_router.callback_query(lambda c: c.data and c.data == "start_post")
async def post_activity(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # Убираем индикатор загрузки
    await callback.message.delete_reply_markup()  # Убираем кнопки у сообщения
    await callback.message.answer(
        "Отлично! Мы поможем вам разместить ваше мероприятие."
    )
    await start_post_session(callback.message, state)


# Обработчик для кнопки "Личный кабинет"
@start_router.callback_query(lambda c: c.data and c.data == "view_account")
async def view_account(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await start_account_session(callback.message, state)
