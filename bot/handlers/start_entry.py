

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

search_button_text = "Искать мероприятия"
post_button_text = "Разместить свое мероприятие"
view_account_text = "Открыть личный кабинет"
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

3. {view_account_text}: Вы хотите открыть личный кабинет и просмотреть ваши бронирования? Выберите эту опцию, и мы поможем вам сделать это.

Если у вас есть вопросы или нужна помощь, просто напишите нам — мы всегда рады помочь!
"""

start_buttons = [
    [InlineKeyboardButton(text=search_button_text, callback_data="start_search")],
    [InlineKeyboardButton(text=post_button_text, callback_data="start_post")],
    [InlineKeyboardButton(text=view_account_text, callback_data="view_account")],
]
start_markup = InlineKeyboardMarkup(inline_keyboard=start_buttons)


async def start_entry(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(welcome_message, reply_markup=start_markup)