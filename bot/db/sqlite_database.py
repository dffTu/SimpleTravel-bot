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
        post_id, author_id, name, date, region, photos, contacts = value
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        photos = literal_eval(photos)
        return constants.Post(
            id=post_id,
            info=constants.PostInfo(author_id, name, date, region, photos, contacts))

    def add_post(self, info: constants.PostInfo) -> bool:
        # TODO: handle exceptions
        self.cursor.execute(
            "INSERT INTO Posts (author_id, name, date, region, photos, contacts) VALUES (?, ?, ?, ?, ?, ?)",
            (info.author_id, info.name, str(info.date), info.region, str(info.photos), info.contacts),
        )
        self.db.commit()
        return True

    def get_posts(self, info: constants.SearchInfo) -> list[constants.Post]:
        self.cursor.execute(
            "SELECT id, author_id, name, date, region, photos, contacts FROM Posts WHERE region LIKE ? AND date = ?",
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

    def book_event(self, chat_id: int, post_id: int) -> bool:
        if self.get_user(chat_id) is None:
            return False
        self.cursor.execute(
            "SELECT * FROM Posts WHERE id = ?",
            (post_id, )
        )
        post = self.cursor.fetchone()
        if post is None:
            return False
        self.cursor.execute(
            "INSERT INTO Bookings (post_id, user_id) VALUES (?, ?)",
            (post_id, chat_id),
        )
        self.db.commit()
        return True

    def get_bookings_by_author(self, chat_id: int) -> list[constants.BookingInfo]:
        self.cursor.execute(
            """
            SELECT b.post_id, b.user_id
            FROM Bookings b
            JOIN Posts p ON p.id = b.post_id
            WHERE p.author_id = ?
            """,
            (chat_id,)
        )
        bookings = self.cursor.fetchall()
        return [constants.BookingInfo(post_id, user_id) for (post_id, user_id) in bookings]

    def get_bookings_by_client(self, chat_id: int) -> list[constants.BookingInfo]:
        self.cursor.execute(
            "SELECT post_id, user_id FROM Bookings WHERE user_id = ?",
            (chat_id,)
        )
        bookings = self.cursor.fetchall()
        return [constants.BookingInfo(post_id, user_id) for (post_id, user_id) in bookings]

    def __del__(self):
        self.db.close()
