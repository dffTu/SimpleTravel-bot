class PostInfo:
    def __init__(self, name: str, date: str, region: str, photos: list[str], contacts: str):
        self.name = name
        self.date = date
        self.region = region
        self.photos = photos
        self.contacts = contacts


class SearchInfo:
    def __init__(self, date: str, region: str):
        self.date = date
        self.region = region
