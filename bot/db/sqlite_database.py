import sqlite3
from typing import Any
from bot.db.template_database import Database
from bot.db.constants import PostInfo, SearchInfo


class SQLiteDatabase(Database):
    def __init__(self, path: str):
        self.path = path
        self.db = sqlite3.connect(self.path)
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Posts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            region TEXT NOT NULL,
            photos TEXT NOT NULL,
            contacts TEXT NOT NULL
            )
        ''')
        self.db.commit()

    def add_post(self, info: PostInfo):
        self.cursor.execute('INSERT INTO Posts (name, date, region, photos, contacts) VALUES (?, ?, ?, ?, ?)',
                            (info.name, info.date, info.region, str(info.photos), info.contacts))
        self.db.commit()

    def get_posts(self, info: SearchInfo) -> list[Any]:
        self.cursor.execute('SELECT * FROM Posts WHERE region = ? AND date = ?', (info.region, info.date))
        posts = self.cursor.fetchall()
        return posts

    def __del__(self):
        self.db.close()
