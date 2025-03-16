from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostInfo:
    author_id: int
    name: str
    date: datetime
    region: str
    photos: list[str]
    contacts: str


@dataclass
class SearchInfo:
    name: str = None
    date_start: datetime = None
    date_end: datetime = None
    region: str = None
    area_km: float = 10


@dataclass
class UserInfo:
    chat_id: int
    name: str
    phone_number: str
    email: str


@dataclass
class Post:
    id: int
    info: PostInfo


@dataclass
class BookingInfo:
    post_id: int
    user_id: int
