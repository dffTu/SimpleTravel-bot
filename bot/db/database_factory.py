from decouple import config
from db.sqlite_database import SQLiteDatabase
from db.template_database import Database


def createDatabase() -> Database:
    return SQLiteDatabase(config("SQLitePath", default='db/example_db.db'))