import asyncio
from datetime import datetime
import logging
from operator import call
from typing import Any, Dict
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser


search_router = Router()


class SearchForm(StatesGroup):
    date_question = State()
    region_qestion = State()


async def startSearchSession(callback: types.CallbackQuery, state: FSMContext):
    await asyncio.sleep(1.2)
    await callback.message.answer("Введите желаемую дату мероприятия")
    logging.info(f'Set date_question state for user with id {callback.from_user.id}')
    await state.set_state(SearchForm.date_question)


@search_router.message(SearchForm.date_question)
async def processDate(message: types.Message, state: FSMContext):
    date: datetime
    try:
        date = parser.parse(message.text)
    except ValueError:
        message.answer(
            "Не удалось распознать введенную дату. Попробуйте ввести в формате YYYY-MM-DD"
        )
        return
    await state.update_data(date=date)

    await message.answer("Введите желаемый регион мероприятия")
    await state.set_state(SearchForm.region_qestion)


@search_router.message(SearchForm.region_qestion)
async def processRegion(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    data = await state.get_data()
    await doSearch(message, **data)
    await state.clear()


async def doSearch(message: types.Message, date: datetime, region: str):
    await message.answer(f"Введенные данные: дата: {date}, регион: {region}")
