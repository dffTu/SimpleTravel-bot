import bot.db.constants as constants
from typing import Union


class Database:
    def add_post(self, info: constants.PostInfo) -> bool:
        pass

    def get_posts(self, info: constants.SearchInfo) -> list[constants.PostInfo]:
        pass

    def get_user(self, chat_id: int) -> Union[None, constants.UserInfo]:
        pass

    def add_user(self, info: constants.UserInfo) -> bool:
        pass
