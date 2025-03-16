import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from bot.db.database_factory import create_database


logging.basicConfig(
    level=config("LOGLEVEL", default=logging.INFO),format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

admins = [int(admin_id) for admin_id in config("ADMINS").split(",")]
database = create_database()

# Определяем токен отдельно для использования в других модулях
BOT_TOKEN = config("TOKEN")

# Создаем глобальные объекты бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Экспортируем все необходимые переменные
__all__ = ['bot', 'dp', 'BOT_TOKEN', 'admins', 'database']
