import csv
import logging
from pathlib import Path
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from supergood_reads.models import Book, Country, Film, Genre

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Load Film and Book fixture data from csv files.

    Loads titles in one at a time because bulk_create does not work well with
    ManyToMany Relationships.

    In order to bulk_create the Through models that join Films/Books to their M2M
    related genres and countries, we would need to have access to all of the created
    objects' primary keys.

    However, bulk_create does not return primary keys for several databases, including
    the default version of sqlite3 that is installed with MacOS.

    The naive implementation is fast for our dataset, so we're not going to worry about
    it.
    """

    help = "Load fixture data"
    batch_size = 1000

    def handle(self, *args: Any, **options: Any) -> None:
        self.verbosity = options.get("verbosity", 0)
        self.load_films("bfi_2022")
        self.load_films("bfi_2022_directors")
        self.load_films("imdb_top_1000")
        self.load_books("7k_books")
        self.success()

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "verbose", nargs="?", type=bool, help="Log every title that is loaded"
        )

    def get_csv_filepath(self, filename: str) -> Path:
        app_config = apps.get_app_config("supergood_reads")
        filepath = Path(app_config.path) / "data" / f"{filename}.csv"
        return filepath

    @transaction.atomic
    def load_films(self, filename: str) -> None:
        logger.info(f"~~~~ Loading {filename} films")
        with open(self.get_csv_filepath(filename), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self.verbosity >= 2:
                    logger.info(f"     {row['title']}")

                genre_instances = []
                country_instances = []

                # Create film
                film = Film.objects.get_or_create(
                    title=row["title"],
                    year=int(row["year"]),
                    defaults={
                        "director": row["director"],
                        "validated": True,
                    },
                )[0]

                # Add genres
                for genre in row["genres"].split(";"):
                    if genre:
                        genre_instances.append(
                            Genre.objects.get_or_create(
                                name=genre,
                            )[0]
                        )
                film.genres.add(*genre_instances)

                # countries
                for country in row["countries"].split(";"):
                    if country:
                        country_instances.append(
                            Country.objects.get_or_create(name=country)[0]
                        )
                film.countries.add(*country_instances)

    @transaction.atomic
    def load_books(self, filename: str) -> None:
        logger.info(f"~~~~ Loading {filename} books")
        with open(self.get_csv_filepath(filename), newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self.verbosity >= 2:
                    logger.info(f"     {row['title']}")

                genre_instances = []

                # Create book
                book = Book.objects.get_or_create(
                    title=row["title"],
                    author=row["author"],
                    defaults={
                        "validated": True,
                        "year": row["year"],
                        "pages": row["pages"] or None,
                    },
                )[0]

                # Add genres
                for genre in row["genres"].split(";"):
                    if genre:
                        genre_instances.append(
                            Genre.objects.get_or_create(
                                name=genre,
                            )[0]
                        )
                book.genres.add(*genre_instances)

    def success(self) -> None:
        logger.info("Fixtures loaded sucessfully")
