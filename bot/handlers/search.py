import asyncio
from datetime import datetime
import logging
from aiogram import Router, types
from aiogram.exceptions import TelegramEntityTooLarge, TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser
from bot.globals import database
import bot.db.constants as constants
from urllib.parse import urlencode


search_router = Router()

search_end_keybord = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Искать еще", callback_data="search_more")]
    ]
)


class SearchForm(StatesGroup):
    date_question = State()
    region_qestion = State()


async def start_search_session(message: types.Message, state: FSMContext):
    logging.debug(f"starting search session for user with id {message.from_user.id}")
    await asyncio.sleep(0.4)
    await message.answer("Введите желаемую дату мероприятия.")
    await state.set_state(SearchForm.date_question)


@search_router.message(SearchForm.date_question)
async def process_date(message: types.Message, state: FSMContext):
    date: datetime
    try:
        date = parser.parse(message.text)
    except ValueError:
        await message.answer(
            "Не удалось распознать введенную дату. Попробуйте ввести в формате YYYY-MM-DD."
        )
        return
    await state.update_data(date=date)

    await message.answer("Введите желаемый регион мероприятия.")
    await state.set_state(SearchForm.region_qestion)


@search_router.message(SearchForm.region_qestion)
async def process_region(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["region"] = message.text

    found_posts = await do_search(message, state, **data)
    if found_posts:
        await state.clear()
    else:
        await start_search_session(message, state)


async def do_search(
    message: types.Message, state: FSMContext, date: datetime, region: str
) -> bool:
    search_info = constants.SearchInfo(date, region)
    logging.debug(search_info)
    posts = database.get_posts(search_info)
    logging.debug(f"posts={posts}")
    if not posts:
        await message.answer(
            "К сожалению, мы не нашли мероприятий, соответствующих вашим фильтрам. Попробуйте изменить параметры поиска или зайдите позже."
        )
        return False

    MAX_POSTS = 4
    posts = posts[:MAX_POSTS]
    for post in posts:
        text = (
            f"🌴 Название мероприятия: {post.info.name}\n"
            f"📆 Дата: {post.info.date}\n"
            f"📍 Место: {post.info.region}\n"
            f"✉️ Контакт: {post.info.contacts}\n"
        )

        should_send_text = True
        if post.info.photos:
            should_send_text = False
            media = [
                types.InputMediaPhoto(media=types.URLInputFile(image_url))
                for image_url in post.info.photos
            ]

            # Добавляем текст к первой фотографии
            media[0].caption = text
            media[0].parse_mode = "HTML"

            # Отправляем группу медиа
            try:
                await message.answer_media_group(media)
            except (TelegramNetworkError, TelegramEntityTooLarge) as e:
                logging.error(f"Error during uploading photos: {e.message}")
                should_send_text = True

        if should_send_text:
            # Если фотографий нет или при их отправке произошла ошибка просто отправляем текст
            await message.answer(text)

    # Отправляем клавиатуру в отдельном сообщении
    await message.answer("Что хотите делать дальше?", reply_markup=search_end_keybord)
    return True


# Обработчик callback для кнопки "Искать еще"
@search_router.callback_query(lambda c: c.data and c.data == "search_more")
async def process_search_more(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup(),  # Убираем кнопки у сообщения
    await callback.message.answer("Начинаем новый поиск...")
    await start_search_session(callback.message, state)
