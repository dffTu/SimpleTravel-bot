from decouple import config
from bot.db.sqlite_database import SQLiteDatabase
from bot.db.template_database import Database


def create_database() -> Database:
    return SQLiteDatabase(config("SQLitePath", default='db/example_db.db'))
