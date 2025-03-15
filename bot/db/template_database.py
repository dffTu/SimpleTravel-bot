import bot.db.constants as constants
from typing import Union


class Database:
    def add_post(self, info: constants.PostInfo) -> bool:
        pass

    def get_posts(self, info: constants.SearchInfo) -> list[constants.Post]:
        pass

    def get_user(self, chat_id: int) -> Union[None, constants.UserInfo]:
        pass

    def add_user(self, info: constants.UserInfo) -> bool:
        pass

    def book_event(self, chat_id: int, post_id: int) -> bool:
        pass

    def get_bookings_by_author(self, chat_id: int) -> list[constants.BookingInfo]:
        pass

    def get_bookings_by_client(self, chat_id: int) -> list[constants.BookingInfo]:
        pass
