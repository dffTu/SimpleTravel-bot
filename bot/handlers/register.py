

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.db.constants import UserInfo
from bot.globals import database
from bot.handlers.start_entry import back_to_start

register_router = Router()


async def check_registration(message: Message) -> bool:
    user_info = database.get_user(message.from_user.id)
    return user_info is not None


class RegisterForm(StatesGroup):
    name_question = State()
    phone_question = State()
    email_question = State()

async def start_register_session(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegisterForm.name_question)
    await message.answer("Введите ваше имя.")


@register_router.message(RegisterForm.name_question)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона.")
    await state.set_state(RegisterForm.phone_question)


@register_router.message(RegisterForm.phone_question)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите ваш email.")
    await state.set_state(RegisterForm.email_question)


@register_router.message(RegisterForm.email_question)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    data = await state.get_data()
    user_info = UserInfo(
        chat_id=message.from_user.id,
        name=data["name"],
        phone_number=data["phone"],
        email=data["email"]
    )
    is_added = database.add_user(user_info)
    if is_added:
        answer = await message.answer("Вы успешно зарегистрировались.")
        await back_to_start(answer, state)
    else:
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")
        await start_register_session(message, state)

