import asyncio
from aiogram.types import BotCommand

from bot.globals import bot, dp
import bot.handlers as handlers

routers = [
    handlers.start_router,
    handlers.post_router,
    handlers.search_router
]

commands = [
    BotCommand(command='start', description='Перейти к главному меню бота')
]


async def main():
    dp.include_routers(*routers)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands, language_code='ru')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
