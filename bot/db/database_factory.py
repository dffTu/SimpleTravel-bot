from decouple import config
from bot.db.sqlite_database import SQLiteDatabase
from bot.db.template_database import Database

from pathlib import Path


def create_database() -> Database:
    return SQLiteDatabase(config("SQLitePath", default=Path(__file__).parent / 'example_db.db'))
