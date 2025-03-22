
import logging
from typing import Optional, Union
from aiogram.methods import TelegramMethod
from aiogram.types import InputMediaPhoto, Message, URLInputFile, InlineKeyboardMarkup
from aiogram.exceptions import TelegramEntityTooLarge, TelegramNetworkError
from bot.db.constants import PostInfo


async def send_post(message: Message, post: PostInfo, keyboard: InlineKeyboardMarkup):
    text = (
        f"🌴 Название мероприятия: {post.name}\n"
        f"📆 Дата: {post.date}\n"
        f"📍 Место: {post.region}\n"
        f"✉️ Контакт: {post.contacts}\n"
    )

    should_send_text = True
    if post.photos:
        should_send_text = False
        media = [
            InputMediaPhoto(media=URLInputFile(image_url))
            for image_url in post.photos
        ]

        # Добавляем текст к первой фотографии
        media[0].caption = text
        media[0].parse_mode = "HTML"

        # Отправляем группу медиа с кнопкой
        try:
            return await message.answer_media_group(media, reply_markup=keyboard)
        except (TelegramNetworkError, TelegramEntityTooLarge) as e:
            logging.error(f"Error during uploading photos: {e.message}")
            should_send_text = True

    if should_send_text:
        # Если фотографий нет или при их отправке произошла ошибка, просто отправляем текст с кнопкой
        return await message.answer(text, reply_markup=keyboard)
