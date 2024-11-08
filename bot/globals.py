from email.policy import default
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from bot.db.database_factory import create_database


logging.basicConfig(
    level=config("LOGLEVEL", default=logging.INFO), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

admins = [int(admin_id) for admin_id in config("ADMINS").split(",")]
database = create_database()
bot = Bot(
    token=config("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
