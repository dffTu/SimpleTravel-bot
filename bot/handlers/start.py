import asyncio
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.handlers.search import startSearchSession

search_button_text = "Искать мероприятия"
post_button_text = "Разместить свое мероприятие"
welcome_message = f"""
🌍 Добро пожаловать в SimpleTravel!

Рады приветствовать вас в SimpleTravel — вашем универсальном помощнике для поиска, размещения и бронирования разнообразных активностей, включая туры, экскурсии, концерты и многое другое.

🔍 Что мы предлагаем:

- Поиск и Бронирование: Легко находите и бронируйте активности, которые вам интересны.
- Размещение Ваших Активностей: У вас есть уникальное мероприятие? Разместите его у нас и привлекайте больше участников!
- Разнообразие: Богатый выбор мероприятий и аттракций на любой вкус.
- Удобная Фильтрация: Используйте наши фильтры, чтобы быстро и без лишних хлопот найти именно то, что вам нужно.

❗ Как начать:

1. {search_button_text}: Выберите эту опцию для просмотра и бронирования доступных активностей.

2. {post_button_text}: Хотите разместить свое мероприятие? Выберите эту опцию, и мы поможем вам начать.

Если у вас есть вопросы или нужна помощь, просто напишите нам — мы всегда рады помочь!
"""

start_router = Router()

start_buttons = [
    [InlineKeyboardButton(text=search_button_text, callback_data="search")],
    [InlineKeyboardButton(text=post_button_text, callback_data="post")],
]
start_markup = InlineKeyboardMarkup(inline_keyboard=start_buttons)


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(welcome_message, reply_markup=start_markup)


# Обработчик для кнопки "Искать мероприятия"
@start_router.callback_query(lambda c: c.data and c.data.startswith("search"))
async def search_activities(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(),  # Убираем индикатор загрузки
    await callback.message.delete_reply_markup(),  # Убираем кнопки у сообщения
    await callback.message.answer(
        "Прекрасно! Давайте найдем для вас что-то интересное..."
    ),
    await startSearchSession(callback.message, state)



# Обработчик для кнопки "Разместить свое мероприятие"
@start_router.callback_query(lambda c: c.data and c.data.startswith("post"))
async def post_activity(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(),  # Убираем индикатор загрузки
    await callback.message.delete_reply_markup(),  # Убираем кнопки у сообщения
    await callback.message.answer(
        "Отлично! Мы поможем вам разместить ваше мероприятие. (Пока все)"
    ),
