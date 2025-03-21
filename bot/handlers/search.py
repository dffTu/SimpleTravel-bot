import asyncio
from datetime import datetime
import logging
from typing import Any, Dict
from aiogram import Router, types
from aiogram.exceptions import TelegramEntityTooLarge, TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser
from bot.globals import database
import bot.db.constants as constants
from urllib.parse import urlencode

from bot.handlers.start_entry import back_to_start


search_router = Router()

search_end_keybord = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [types.InlineKeyboardButton(text="Искать еще", callback_data="search_more")],
        [types.InlineKeyboardButton(text="Вернуться на главный экран", callback_data="go_back")]
    ]
)


class SearchForm(StatesGroup):
    main_menu = State()
    date_start_question = State()
    date_end_question = State()
    region_qestion = State()
    area_question = State()
    name_question = State()

async def update_markup(data: Dict[str, Any]):
    if not 'answer_message' in data:
        return
    answer_message = data['answer_message']

    date_start_button = types.InlineKeyboardButton(text=f"{'✅' if 'date_start' in data else '❌'}Дата начала: {data.get('date_start').date() if 'date_start' in data else 'Любая'}", callback_data="filter_date_start")
    date_end_button = types.InlineKeyboardButton(text=f"{'✅' if 'date_end' in data else '❌'}Дата окончания: {data.get('date_end').date() if 'date_end' in data else 'Любая'}", callback_data="filter_date_end")
    region_button = types.InlineKeyboardButton(text=f"{'✅' if 'region' in data else '❌'}Регион: {data.get('region', 'Любой')}", callback_data="filter_region")
    area_button = types.InlineKeyboardButton(text=f"{'✅' if 'area_km' in data else '❌'}Расстояние: {data.get('area_km', 'Любое')}", callback_data="filter_area")
    name_button = types.InlineKeyboardButton(text=f"{'✅' if 'name' in data else '❌'}Название мероприятия: {data.get('name', 'Любое')}", callback_data="filter_name")

    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [name_button],
        [date_start_button, date_end_button],
        [region_button, area_button],
        [types.InlineKeyboardButton(text="Начать поиск", callback_data="do_search")],
        [types.InlineKeyboardButton(text="Вернуться на главный экран", callback_data="go_back")]
    ])


    await answer_message.edit_reply_markup(reply_markup=markup)


async def start_search_session(message: types.Message, state: FSMContext):
    logging.debug(f"starting search session for user with id {message.from_user.id}")
    await state.clear()

    answer = await message.answer("Выберите фильтры для поиска:")
    data = await state.update_data(answer_message=answer)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)


@search_router.callback_query(lambda c: c.data == 'filter_date_start')
async def filter_date_start(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите желаемую дату начала мероприятия.")
    await state.set_state(SearchForm.date_start_question)


@search_router.message(SearchForm.date_start_question)
async def process_date_start(message: types.Message, state: FSMContext):
    try:
        date_start = parser.parse(message.text)
    except ValueError:
        await message.answer(
            "Не удалось распознать введенную дату. Попробуйте ввести в формате YYYY-MM-DD."
        )
        return
    data = await state.update_data(date_start=date_start)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)


@search_router.callback_query(lambda c: c.data == 'filter_date_end')
async def filter_date_end(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите желаемую дату окончания мероприятия.")
    await state.set_state(SearchForm.date_end_question)


@search_router.message(SearchForm.date_end_question)
async def process_date_end(message: types.Message, state: FSMContext):
    try:
        date_end = parser.parse(message.text)
    except ValueError:
        await message.answer(
            "Не удалось распознать введенную дату. Попробуйте ввести в формате YYYY-MM-DD."
        )
        return
    data = await state.update_data(date_end=date_end)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)


@search_router.callback_query(lambda c: c.data == 'filter_region')
async def filter_region(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите желаемый регион мероприятия.")
    await state.set_state(SearchForm.region_qestion)

@search_router.message(SearchForm.region_qestion)
async def process_region(message: types.Message, state: FSMContext):
    data = await state.update_data(region=message.text)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)


@search_router.callback_query(lambda c: c.data == 'filter_area')
async def filter_area(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите желаемый радиус поиска в километрах.")
    await state.set_state(SearchForm.area_question)

@search_router.message(SearchForm.area_question)
async def process_area(message: types.Message, state: FSMContext):
    try:
        area_km = float(message.text)
    except ValueError:
        await message.answer("Не удалось распознать введенное значение. Попробуйте ввести число.")
        return
    data = await state.update_data(area_km=area_km)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)

@search_router.callback_query(lambda c: c.data == 'filter_name')
async def filter_name(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Введите желаемое название мероприятия.")
    await state.set_state(SearchForm.name_question)

@search_router.message(SearchForm.name_question)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.update_data(name=message.text)
    await update_markup(data)
    await state.set_state(SearchForm.main_menu)


@search_router.callback_query(lambda c: c.data == 'do_search')
async def do_search(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    found_posts = await handle_search(callback_query.message, **data)
    if found_posts:
        await state.clear()
    else:
        await start_search_session(callback_query.message, state)


async def handle_search(
    message: types.Message, **kwargs
) -> bool:
    params = {}
    for key in ['name', 'date_start', 'date_end', 'region', 'area_km']:
        if key in kwargs:
            params[key] = kwargs.get(key)
    logging.debug(f'params={params}')
    search_info = constants.SearchInfo(**params)
    logging.debug(f'search_info={search_info}')
    posts = database.search_posts(search_info)
    logging.debug(f'posts={posts}')
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

        button = types.InlineKeyboardButton(text="Записаться", callback_data=f"book_event_{post.id}")
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])

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

            # Отправляем группу медиа с кнопкой
            try:
                await message.answer_media_group(media)
                await message.answer("", reply_markup=keyboard)  # Отправляем кнопку отдельно
            except (TelegramNetworkError, TelegramEntityTooLarge) as e:
                logging.error(f"Error during uploading photos: {e.message}")
                should_send_text = True

        if should_send_text:
            # Если фотографий нет или при их отправке произошла ошибка, просто отправляем текст с кнопкой
            await message.answer(text, reply_markup=keyboard)

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


@search_router.callback_query(lambda c: c.data and c.data.startswith('book_event_'))
async def handle_booking(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    post_id = int(callback_query.data.split('_')[2])  # Извлекаем ID поста из callback_data

    success = database.book_event(user_id, post_id)
    if success:
        await callback_query.answer("Вы успешно записались на мероприятие!")
    else:
        await callback_query.answer("Вы уже записались на это мероприятие.")


@search_router.callback_query(lambda c: c.data == 'go_back')
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await back_to_start(callback.message, state)
    await callback.answer()
