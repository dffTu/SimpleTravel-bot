import sqlite3
import datetime
from ast import literal_eval
from bot.db.template_database import Database
import bot.db.constants as constants
from typing import Union
import os
from pathlib import Path


class SQLiteDatabase(Database):
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.cursor = self.db.cursor()

        scripts_path = Path(__file__).parent / "sql_scripts"
        scripts = [os.path.join(dirpath, f) for (dirpath, _, filenames)
                   in os.walk(scripts_path) for f in filenames]

        for script in sorted(scripts):
            self.cursor.execute(open(script, "r").read())

        # TODO: сделать индекс на столбцах по которым делаем select?
        self.db.commit()

    def parse_post_info(self, value: tuple):
        name, date, region, photos, contacts = value[1:]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        photos = literal_eval(photos)
        return constants.PostInfo(name, date, region, photos, contacts)

    def add_post(self, info: constants.PostInfo) -> bool:
        # TODO: handle exceptions
        self.cursor.execute(
            "INSERT INTO Posts (author_id, name, date, region, photos, contacts) VALUES (?, ?, ?, ?, ?, ?)",
            (info.author_id, info.name, str(info.date), info.region, str(info.photos), info.contacts),
        )
        self.db.commit()
        return True

    def get_posts(self, info: constants.SearchInfo) -> list[constants.PostInfo]:
        self.cursor.execute(
            "SELECT * FROM Posts WHERE region LIKE ? AND date = ?",
            ('%' + info.region + '%', info.date),
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def get_user(self, chat_id: int) -> Union[None, constants.UserInfo]:
        self.cursor.execute(
            "SELECT chat_id, name, phone_number, email FROM Users WHERE chat_id = ?",
            (chat_id,)
        )
        user = self.cursor.fetchone()
        if user is None:
            return None
        return constants.UserInfo(chat_id=user[0], name=user[1], phone_number=user[2], email=user[3])

    def add_user(self, info: constants.UserInfo) -> bool:
        if self.get_user(info.chat_id) is not None:
            return False
        self.cursor.execute(
            "INSERT INTO Users (chat_id, name, phone_number, email) VALUES (?, ?, ?, ?)",
            (info.chat_id, info.name, info.phone_number, info.email),
        )
        self.db.commit()
        return True

    def __del__(self):
        self.db.close()
