import csv
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from django_flex_reviews.media_types.models import Book, Country, Film, Genre


@dataclass
class ThroughModelData:
    """Contains instructions for how to build ThroughModel"""

    film_index: int
    genre_start_index: Optional[int] = None
    genre_end_index: int
    country_start_index: Optional[int] = None
    country_end_index: Optional[int] = None


class LoadFilms:
    batch_size = 1000

    def __init__(self, filename: str):
        self.filename = filename
        self.genres: list[Genre] = []
        self.countries: list[Country] = []
        self.films: list[Film] = []
        self.through_model_data: list[ThroughModelData] = []

    def run(self):
        self.read_csv_data()

    @transaction.atomic
    def commit(self):
        self.bulk_create_genres()
        self.bulk_create_countries()
        self.bulk_create_films()
        self.bulk_create_through()

    def read_csv_data(self):
        with open(self.get_csv_file(self.filename), newline="") as f:
            reader = csv.DictReader(f)
            genre_total = 0
            country_total = 0
            for row in reader:
                genres_in_row = 0
                countries_in_row = 0
                # Get Film from csv row
                self.films.append(
                    Film(
                        title=row["title"],
                        release_year=int(row["year"]),
                        director=row["director"],
                    )
                )
                # Get Genres from csv row
                for genre in row["genres"].split(";"):
                    if genre:
                        self.genres.add(Genre(genre=genre))
                        genres_in_row += 1
                # Get Countries from csv row
                for country in row["countries"].split(";"):
                    if country:
                        self.countries.add(Country(name=country))
                        countries_in_row += 1
                # Add ThroughModel data for ManyToMany relationships
                self.self.through_model_data.append(
                    ThroughModelData(
                        genre_start_index=genre_total,
                        genre_end_index=genre_total + genres_in_row,
                        country_start_index=country_total,
                        country_end_index=country_total + countries_in_row,
                    )
                )
                genre_total += genres_in_row
                country_total += countries_in_row

    def bulk_create_genres(self):
        self.created_genres = Genre.objects.bulk_create(
            list(self.genres),
            ignore_conflicts=True,
            unique_fields=["genre"],
            batch_size=self.batch_size,
        )

    def bulk_create_countries(self):
        self.created_countries = Country.objects.bulk_create(
            list(self.countries),
            ignore_conflicts=True,
            unique_fields=["name"],
            batch_size=self.batch_size,
        )

    def bulk_create_films(self):
        self.created_films = Film.objects.bulk_create(
            self.films,
            ignore_conflicts=True,
            unique_fields=["title", "year"],
            batch_size=self.batch_size,
        )

    def bulk_create_through(self):
        ThroughModel = Film.objects.through  # noqa: N806
        through_instances = []
        # for i, film in self.created_films.items():
        # through_instances.append()
        ThroughModel.objects.bulk_create(
            through_instances,
            batch_size=self.batch_size,
        )


class Command(BaseCommand):
    """Load fixture data from csv files.

    Loads titles in one at a time because bulk_create does not work with
    ManyToMany Relationships.

    To bulk_create the Through models that join Films/Books to their M2M related genres
    and countries, we would need to have access to all created objects' primary keys.

    bulk_create does not return primary keys for several databases, including the
    default version of sqlite3 that is installed with MacOS.



    """

    help = "Load fixture data"
    batch_size = 1000

    def handle(self, *args, **kwargs):
        self.load_films("bfi_2022")
        self.load_films("bfi_2022_directors")
        self.load_films("imdb_top_1000")
        self.load_books("goodreads")

    def get_csv_file(self, filename: str):
        return settings.PROJECT_ROOT / "tests" / "data" / f"{filename}.csv"

    def bulk_create_films(self, bound_films: list[Film], film_count: int):
        Film.objects.bulk_create(
            bound_films,
            ignore_conflicts=True,
            unique_fields=["title", "year"],
            batch_size=self.batch_size,
        )
        print(f"{film_count} films loaded.")

    @transaction.atomic
    def load_films(self, filename):
        print(f"~~~~ Loading {filename} films")
        film_count = 0
        bound_films = []
        with open(self.get_csv_file(filename), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"~~~~ Processing {row['title']}")
                film_count += 1
                bound_film = Film(
                    title=row["title"],
                    release_year=int(row["year"]),
                    director=row["director"],
                )
                bound_film.genres.add(
                    *[Genre(genre=genre) for genre in row["genres"].split(";") if genre]
                )
                bound_film.countries.add(
                    *[
                        Country(name=country)
                        for country in row["countries"].split(";")
                        if country
                    ]
                )
        self.bulk_create_films(bound_films, film_count)

    def bulk_create_books(self, bound_books: list[Book], book_count: int):
        Book.objects.bulk_create(
            bound_books,
            ignore_conflicts=True,
            unique_fields=["title", "author"],
            batch_size=self.batch_size,
        )
        print(f"{book_count} books loaded.")

    @transaction.atomic
    def load_books(self, filename):
        print(f"~~~~ Loading {filename} books")
        book_count = 0
        bound_books = []
        with open(self.get_csv_file(filename), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book_count += 1
                bound_book = Book(
                    title=row["title"],
                    publication_year=row["year"],
                    author=row["author"],
                    pages=row["pages"],
                )
                bound_book.genres.add(
                    *[Genre(genre=genre) for genre in row["genres"].split(";") if genre]
                )
                bound_books.append(bound_book)
        self.bulk_create_books(bound_books, book_count)
