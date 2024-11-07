from dataclasses import dataclass


@dataclass
class PostInfo:
    name: str
    date: str
    region: str
    photos: list[str]
    contacts: str


@dataclass
class SearchInfo:
    date: str
    region: str
