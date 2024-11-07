import asyncio
from datetime import datetime
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser
from bot.create_bot import database
from bot.db.constants import SearchInfo


search_router = Router()


class SearchForm(StatesGroup):
    date_question = State()
    region_qestion = State()


async def startSearchSession(message: types.Message, state: FSMContext):
    await asyncio.sleep(1.2)
    await message.answer("Введите желаемую дату мероприятия.")
    logging.info(f"Set date_question state for user with id {message.from_user.id}")
    await state.set_state(SearchForm.date_question)


@search_router.message(SearchForm.date_question)
async def processDate(message: types.Message, state: FSMContext):
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
async def processRegion(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    data = await state.get_data()
    found_posts = await doSearch(message, state, **data)
    if found_posts:
        await state.clear()
    else:
        await startSearchSession(message, state)


async def doSearch(
    message: types.Message, state: FSMContext, date: datetime, region: str
) -> bool:
    search_info = SearchInfo(date.strftime("%d.%m.%Y"), region)
    logging.debug(f"search_info=date:{search_info.date},region={search_info.region}")
    posts = database.get_posts(SearchInfo(date.strftime("%d.%m.%Y"), region))
    logging.debug(f"posts={str(posts)}")
    if not posts:
        await message.answer(
            "К сожалению, мы не нашли мероприятий, соответствующих вашим фильтрам. Попробуйте изменить параметры поиска или зайдите позже."
        )
        return False
    # TODO: support multiple posts
    post = posts[0]
    await message.answer(str(post))
    return True
