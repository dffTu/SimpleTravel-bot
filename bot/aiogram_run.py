import asyncio
import logging
import bot.handlers as handlers
from bot.globals import bot, dp

# Включаем логирование
logging.basicConfig(level=logging.INFO)


async def main():
    # Регистрируем роутеры
    dp.include_router(handlers.start_router)
    dp.include_router(handlers.search_router)
    dp.include_router(handlers.post_router)
    dp.include_router(handlers.account_router)
    dp.include_router(handlers.register_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
