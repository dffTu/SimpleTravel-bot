import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.filters import Command, CommandStart

from bot.db.template_database import Database
from bot.db.constants import UserInfo, BookingInfo, Post
from bot.handlers.start_entry import back_to_start

account_router = Router()

view_subscriptions_text = "Посмотреть мои подписки"
view_user_info_text = "Посмотреть информацию о пользователе"
go_back_text = "Вернуться на главный экран"
account_message = f"""
👤 Личный кабинет

Здесь вы можете управлять своими подписками и просматривать информацию о пользователе.

🔍 Доступные опции:

1. {view_subscriptions_text}: Просмотр ваших подписок на мероприятия.
2. {view_user_info_text}: Просмотр информации о вашем аккаунте.
"""

account_buttons = [
    [InlineKeyboardButton(text=view_subscriptions_text, callback_data="view_subscriptions")],
    [InlineKeyboardButton(text=view_user_info_text, callback_data="view_user_info")],
    [InlineKeyboardButton(text=go_back_text, callback_data="go_back")],
]
account_markup = InlineKeyboardMarkup(inline_keyboard=account_buttons)

class AccountState(StatesGroup):
    MAIN = State()
    VIEW_SUBSCRIPTIONS = State()
    VIEW_USER_INFO = State()

async def start_account_session(message: Message, state: FSMContext):
    await state.set_state(AccountState.MAIN)
    await message.answer(account_message, reply_markup=account_markup)


@account_router.message(Command("account"))
async def cmd_account(message: Message, state: FSMContext):
    await state.set_state(AccountState.MAIN)
    await message.answer(account_message, reply_markup=account_markup)


# Обработчик для кнопки "Посмотреть мои подписки"
@account_router.callback_query(F.data == "view_subscriptions")
async def view_subscriptions(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AccountState.VIEW_SUBSCRIPTIONS)
    db = Database()
    user_id = callback.from_user.id
    bookings = db.get_bookings_by_client(user_id)

    if not bookings:
        message = await callback.message.answer("У вас нет подписок на мероприятия.")
    else:
        subscriptions = "\n".join([f"Мероприятие ID: {booking.post_id}" for booking in bookings])
        message = await callback.message.answer(f"Ваши подписки:\n{subscriptions}")

    await message.edit_reply_markup(reply_markup=account_markup)
    await callback.answer()
    await callback.message.delete_reply_markup()


# Обработчик для кнопки "Посмотреть информацию о пользователе"
@account_router.callback_query(F.data == "view_user_info")
async def view_user_info(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AccountState.VIEW_USER_INFO)
    db = Database()
    user_id = callback.from_user.id
    user_info = db.get_user(user_id)

    if not user_info:
        message = await callback.message.answer("Информация о пользователе не найдена.")
    else:
        user_details = f"""
        👤 Информация о пользователе:
        Имя: {user_info.name}
        Телефон: {user_info.phone_number}
        Email: {user_info.email}
        """
        message = await callback.message.answer(user_details)

    await message.edit_reply_markup(reply_markup=account_markup)
    await callback.answer()
    await callback.message.delete_reply_markup()


# Обработчик для кнопки "Вернуться на главный экран"
@account_router.callback_query(F.data == "go_back")
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    # Здесь вы можете вызвать обработчик главного экрана
    # Например, если у вас есть функция cmd_start для главного экрана:
    await back_to_start(callback.message, state)
    await callback.answer()
