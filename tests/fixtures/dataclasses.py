from dataclasses import dataclass


@dataclass
class FilmData:
    title: str
    year: str
    countries: list[str]
    genres: list[str]
    director: str


@dataclass
class BookData:
    title: str
    author: str
    year: str
    genres: list[str]
    pages: str
