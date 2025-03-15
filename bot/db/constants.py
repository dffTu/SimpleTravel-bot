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
    date: datetime
    region: str


@dataclass
class UserInfo:
    chat_id: int
    name: str
    phone_number: str
    email: str
