import asyncio
from aiogram.types import BotCommand

from bot.globals import bot, dp
from bot.handlers.start import start_router
from bot.handlers.search import search_router
from bot.handlers.post import post_router


async def main():
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(post_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([BotCommand(command='start', description='Go to the main menu')])
    await bot.set_my_commands([BotCommand(command='start', description='Перейти к главному меню бота')], language_code='ru')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
