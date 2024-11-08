from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostInfo:
    name: str
    date: datetime
    region: str
    photos: list[str]
    contacts: str


@dataclass
class SearchInfo:
    date: datetime
    region: str
