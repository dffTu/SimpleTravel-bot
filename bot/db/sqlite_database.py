import sqlite3
import datetime
from ast import literal_eval
from typing import Union
import os
from pathlib import Path

from bot.db.template_database import Database
import bot.db.constants as constants
from bot.utils import geolocations_utils, text_utils, datetime_utils


class SQLiteDatabase(Database):
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.cursor = self.db.cursor()

        scripts_path = Path(__file__).parent / "sql_scripts"
        scripts = [os.path.join(dirpath, f) for (dirpath, _, filenames)
                   in os.walk(scripts_path) for f in filenames]

        self.db.create_function("getTextRatio", 2, text_utils.get_text_ratio)
        self.db.create_function("getDistance", 4, geolocations_utils.get_distance)
        self.db.create_function("insideInterval", 3, datetime_utils.is_date_inside_interval)

        for script in sorted(scripts):
            self.cursor.execute(open(script, "r").read())

        # TODO: сделать индекс на столбцах по которым делаем select?
        self.db.commit()

    def parse_post_info(self, value: tuple):
        post_id, author_id, name, date, region, photos, contacts, is_on_review = value
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        photos = literal_eval(photos)
        return constants.Post(
            id=post_id,
            is_on_review=is_on_review,
            info=constants.PostInfo(author_id, name, date, region, photos, contacts))

    def add_post(self, info: constants.PostInfo) -> bool:
        # TODO: handle exceptions
        lat, lon = geolocations_utils.get_coords(info.region)
        self.cursor.execute(
            "INSERT INTO Posts (author_id, name, date, region, photos, contacts, latitude, longitude)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (info.author_id, info.name, str(info.date), info.region, str(info.photos), info.contacts, lat, lon),
        )
        self.db.commit()
        return True

    def approve_post(self, approver_id: int, post_id: int) -> None:
        user = self.get_user(approver_id)
        if user is None or not user.is_moderator:
            return

        self.cursor.execute(
            "UPDATE Posts SET is_on_review = 0 WHERE id = ?",
            (post_id, ),
        )
        self.db.commit()

    def get_posts_on_review(self, user_id: int) -> list[constants.Post]:
        user = self.get_user(user_id)
        if user is None or not user.is_moderator:
            return []

        self.cursor.execute(
            "SELECT id, author_id, name, date, region, photos, contacts, is_on_review FROM Posts WHERE "
            "is_on_review = 1"
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def search_posts(self, info: constants.SearchInfo) -> list[constants.Post]:
        lat, lon = geolocations_utils.get_coords(info.region)
        self.cursor.execute(
            "SELECT id, author_id, name, date, region, photos, contacts, is_on_review FROM Posts WHERE "
            "is_on_review = 0"
            " AND getTextRatio(?, name) > 80"
            " AND getDistance(?, ?, latitude, longitude) < ?"
            " AND insideInterval(date, ?, ?) = 1",
            (info.name, lat, lon, info.area_km, info.date_start, info.date_end),
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def get_posts_by_author(self, chat_id: int) -> list[constants.Post]:
        self.cursor.execute(
            "SELECT id, author_id, name, date, region, photos, contacts, is_on_review FROM Posts WHERE "
            "author_id = ?",
            (chat_id,)
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def get_user(self, chat_id: int) -> Union[None, constants.UserInfo]:
        try:
            self.cursor.execute(
                "SELECT chat_id, name, phone_number, email, is_moderator FROM Users WHERE chat_id = ?",
                (chat_id,)
            )
            user = self.cursor.fetchone()
            if user is None:
                return None
            return constants.UserInfo(
                chat_id=user[0],
                name=user[1],
                phone_number=user[2],
                email=user[3],
                is_moderator=bool(user[4]))
        except Exception:
            return None

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
            "SELECT * FROM Bookings WHERE post_id = ? AND user_id = ?",
            (post_id, chat_id)
        )
        bookings = self.cursor.fetchall()
        if len(bookings) > 0:
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

    def get_bookings_by_client(self, chat_id: int) -> list[constants.Post]:
        self.cursor.execute(
            """
            SELECT p.id, p.author_id, p.name, p.date, p.region, p.photos, p.contacts, p.is_on_review
            FROM Bookings b
            JOIN Posts p ON p.id = b.post_id
            WHERE b.user_id = ?
            """,
            (chat_id,)
        )
        posts = self.cursor.fetchall()
        posts = list(map(self.parse_post_info, posts))
        return posts

    def __del__(self):
        self.db.close()
