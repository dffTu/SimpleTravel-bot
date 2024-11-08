from bot.db.constants import PostInfo, SearchInfo


class Database:
    def add_post(self, info: PostInfo) -> bool:
        pass

    def get_posts(self, info: SearchInfo) -> list[PostInfo]:
        pass
