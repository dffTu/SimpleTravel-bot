import sqlite3
import datetime
from ast import literal_eval
from bot.db.template_database import Database
from bot.db.constants import PostInfo, SearchInfo


class SQLiteDatabase(Database):
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Posts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            region TEXT NOT NULL,
            photos TEXT NOT NULL,
            contacts TEXT NOT NULL
            )
        """
        )
        # TODO: сделать индекс на столбцах по которым делаем select?
        self.db.commit()

    def parse_post_info(self, value: tuple):
        name, date, region, photos, contacts = value[1:]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        photos = literal_eval(photos)
        return PostInfo(name, date, region, photos, contacts)

    def add_post(self, info: PostInfo) -> bool:
        # TODO: handle exceptions
        self.cursor.execute(
            "INSERT INTO Posts (name, date, region, photos, contacts) VALUES (?, ?, ?, ?, ?)",
            (info.name, str(info.date), info.region, str(info.photos), info.contacts),
        )
        self.db.commit()
        return True

    def get_posts(self, info: SearchInfo) -> list[PostInfo]:
        self.cursor.execute(
            "SELECT * FROM Posts WHERE region LIKE ? AND date = ?",
            (info.region + '%', info.date),
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def __del__(self):
        self.db.close()
