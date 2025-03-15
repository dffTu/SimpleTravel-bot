import asyncio
import datetime
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dateutil import parser

import bot.db.constants as constants
from bot.globals import database


post_router = Router()


class PostForm(StatesGroup):
    name_question = State()
    date_question = State()
    region_question = State()
    photos_question = State()
    contacts_question = State()


async def start_post_session(message: types.Message, state: FSMContext):
    logging.debug(f"starting post session for user with id {message.from_user.id}")
    await asyncio.sleep(0.4)
    await message.answer("Укажите название.")
    await state.set_state(PostForm.name_question)


@post_router.message(PostForm.name_question)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer("Укажите дату.")
    await state.set_state(PostForm.date_question)


@post_router.message(PostForm.date_question)
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

    await message.answer("Укажите регион.")
    await state.set_state(PostForm.region_question)


@post_router.message(PostForm.region_question)
async def process_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)

    await message.answer("Добавьте ссылки на фото через запятую.")
    await state.set_state(PostForm.photos_question)


@post_router.message(PostForm.photos_question)
async def process_photos(message: types.Message, state: FSMContext):
    urls = message.text.split(",")
    urls = list(map(lambda x: x.strip(), urls))

    await state.update_data(photos=urls)

    await message.answer("Добавьте контакты.")
    await state.set_state(PostForm.contacts_question)


@post_router.message(PostForm.contacts_question)
async def process_contacts(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["contacts"] = message.text

    is_succes = await do_post(message, state, **data)
    if is_succes:
        await message.answer(
            "🎉 Ваше мероприятие успешно добавлено!\nМы рады, что вы делитесь с нами вашими интересными событиями. Ожидайте, что ваше мероприятие скоро увидят другие пользователи! Спасибо за ваш вклад!"
        )
        await state.clear()
    else:
        await message.answer(
            "❌ Произошла ошибка при добавлении вашего мероприятия.\nПожалуйста, убедитесь, что вы заполнили все поля корректно и попробуйте еще раз."
        )
        await start_post_session(message, state)


async def do_post(
    message: types.Message,
    state: FSMContext,
    name: str,
    date: datetime,
    region: str,
    photos: list[str],
    contacts: str,
):
    post_info = constants.PostInfo(message.chat.id, name, date, region, photos, contacts)
    return database.add_post(post_info)
