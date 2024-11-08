import asyncio
from datetime import datetime
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser
from bot.create_bot import database
from bot.db.constants import SearchInfo
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
    await asyncio.sleep(0.4)
    await message.answer("Введите желаемую дату мероприятия.")
    logging.info(f"Set date_question state for user with id {message.from_user.id}")
    await state.set_state(SearchForm.date_question)


@search_router.message(SearchForm.date_question)
async def process_date(message: types.Message, state: FSMContext):
    date: datetime
    try:
        date = parser.parse(message.text)
    except ValueError:
        message.answer(
            "Не удалось распознать введенную дату. Попробуйте ввести в формате YYYY-MM-DD."
        )
        return
    await state.update_data(date=date)

    await message.answer("Введите желаемый регион мероприятия.")
    await state.set_state(SearchForm.region_qestion)


@search_router.message(SearchForm.region_qestion)
async def process_region(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    data = await state.get_data()
    found_posts = await do_search(message, state, **data)
    if found_posts:
        await state.clear()
    else:
        await start_search_session(message, state)


async def do_search(
    message: types.Message, state: FSMContext, date: datetime, region: str
) -> bool:
    search_info = SearchInfo(date.strftime("%d.%m.%Y"), region)
    logging.debug(search_info)
    posts = database.get_posts(SearchInfo(date.strftime("%d.%m.%Y"), region))
    logging.debug(f"posts={posts}")
    if not posts:
        await message.answer(
            "К сожалению, мы не нашли мероприятий, соответствующих вашим фильтрам. Попробуйте изменить параметры поиска или зайдите позже."
        )
        return False

    # TODO: support multiple posts
    post = posts[0]
    text = (
        f"🌴 Название мероприятия: {post.name}\n"
        f"📆 Дата: {post.date}\n"
        f"📍 Место: {post.region}\n"
        f"✉️ Контакт: {post.contacts}\n"
    )

    if post.photos:
        # Создаем список InputMediaPhoto
        # TODO: сделать нормально
        media = [
            types.InputMediaPhoto(
                media=types.URLInputFile(
                    "https://upload.wikimedia.org/wikipedia/commons/d/dd/Atlantis_Kircher_Mundus_subterraneus_1678.jpg"
                )
            ),
        ]
        # media = [types.InputMediaPhoto(media=types.URLInputFile(image_url)) for image_url in post.photos]

        # Добавляем текст к первой фотографии
        media[0].caption = text
        media[0].parse_mode = "HTML"

        # Отправляем группу медиа
        await message.answer_media_group(media)
    else:
        # Если фотографий нет, просто отправляем текст
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
