import json
from typing import Any, TypeAlias, TypedDict, Union
from uuid import UUID

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from supergood_review_site.models import Book, Film, GoodreadsStrategy, Review
from supergood_review_site.reviews.forms import CreateNewMediaOption
from supergood_review_site.utils import Utils
from tests.factories import BookFactory, FilmFactory


class FixtureDataItem(TypedDict, total=False):
    id: str
    title: str
    release_year: int
    publication_year: int


FixtureData: TypeAlias = list[FixtureDataItem]


@pytest.fixture
def film_data() -> FixtureData:
    return [
        {
            "id": "e01cdf31-c9d9-432e-a5b7-ac7a0049dd70",
            "title": "Seven Samurai",
            "release_year": 1954,
        },
        {
            "id": "794416b7-d07d-4651-80b6-64eadeea98b1",
            "title": "Steel Magnolias",
            "release_year": 1989,
        },
        {
            "id": "f99ba843-1ba8-4a1d-86c7-5edfd1722655",
            "title": "Charade",
            "release_year": 1963,
        },
    ]


@pytest.fixture
def book_data() -> FixtureData:
    return [
        {
            "id": "e01cdf31-c9d9-432e-a5b7-ac7a0049dd70",
            "title": "Jane Eyre",
            "publication_year": 1847,
        },
        {
            "id": "794416b7-d07d-4651-80b6-64eadeea98b1",
            "title": "The Age of Innocence",
            "publication_year": 1920,
        },
        {
            "id": "f99ba843-1ba8-4a1d-86c7-5edfd1722655",
            "title": "Anna Karenina",
            "publication_year": 1878,
        },
    ]


def cmp(actual: Any, expected: FixtureData) -> bool:
    """Compare just the "id" and "title" fields between two dictionaries."""

    def filter(d: Union[Any, FixtureDataItem]) -> dict[str, Any]:
        return {k: v for k, v in d.items() if k in ["id", "title"]}

    return [filter(d) for d in actual] == [filter(d) for d in expected]


@pytest.mark.django_db
class TestFilmAutocompleteView:
    def test_without_q(self, client: Client, film_data: FixtureData) -> None:
        """Should return all films."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                release_year=data["release_year"],
            )
        url = reverse("film_autocomplete")
        response = client.get(url)
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], film_data)

    def test_with_q(self, client: Client, film_data: FixtureData) -> None:
        """Should only return queried film."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                release_year=data["release_year"],
            )
        url = reverse("film_autocomplete")
        response = client.get(url, {"q": "Charade"})
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], [film_data[2]])


@pytest.mark.django_db
class TestBookAutocompleteView:
    def test_without_q(self, client: Client, book_data: FixtureData) -> None:
        """Should return all films."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                publication_year=data["publication_year"],
            )
        url = reverse("book_autocomplete")
        response = client.get(url)
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], book_data)

    def test_with_q(self, client: Client, book_data: FixtureData) -> None:
        """Should only return queried film."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                publication_year=data["publication_year"],
            )
        url = reverse("book_autocomplete")
        response = client.get(url, {"q": "Anna"})
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], [book_data[2]])


@pytest.mark.django_db
class TestCreateReviewView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("create_review")
        self.book_content_type = Utils.get_content_type_id(Book)
        self.film_content_type = Utils.get_content_type_id(Film)

    @pytest.fixture
    def create_review_data(self) -> dict:
        """dict(request.POST.items()) from CreateReviewView.post"""
        return {
            "review-media_type_content_type": "",
            "review_mgmt-create_new_media_type_object": "",
            "review-media_type_object_id": "",
            "book-title": "",
            "book-author": "",
            "book-publication_year": "",
            "book-pages": "",
            "film-title": "",
            "film-director": "",
            "film-release_year": "",
            "review-completed_at_day": "",
            "review-completed_at_month": "",
            "review-completed_at_year": "",
            "review-strategy_content_type": Utils.get_content_type_id(
                GoodreadsStrategy
            ),
            "ebertstrategy-rating": "",
            "goodreadsstrategy-stars": "5",
            "maximusstrategy-recommended": "",
            "review-text": "It was good.",
        }

    def test_existing_book(self, client: Client, create_review_data: dict):
        book = BookFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["review-media_type_object_id"] = book.id
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review.media_type == book
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_existing_film(self, client: Client, create_review_data: dict):
        film = FilmFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["review-media_type_object_id"] = film.id
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review.media_type == film
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_create_new_book(self, client: Client, create_review_data: dict):
        book = BookFactory.build()  # not saved to database
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["book-title"] = book.title
        create_review_data["book-author"] = book.author
        create_review_data["book-publication_year"] = book.publication_year
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review.media_type.title == book.title

    def test_create_new_film(self, client: Client, create_review_data: dict):
        film = FilmFactory.build()  # not saved to database
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["film-title"] = film.title
        create_review_data["film-director"] = film.director
        create_review_data["film-release_year"] = film.release_year
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review.media_type.title == film.title

    def test_missing_selected_book(self, client: Client, create_review_data: dict):
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that book selection has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        assert (
            soup.find("autocomplete", attrs={"url": "/app/book-autocomplete/"})
            .parent.find("ul", attrs={"class": "errorlist"})
            .find("li")
            .text
        ) == "This field is required."

    def test_missing_selected_film(self, client: Client, create_review_data: dict):
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that book selection has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        assert (
            soup.find("autocomplete", attrs={"url": "/app/film-autocomplete/"})
            .parent.find("ul", attrs={"class": "errorlist"})
            .find("li")
            .text
        ) == "This field is required."

    def test_missing_new_book(self, client: Client, create_review_data: dict):
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["book-title"] = ""
        create_review_data["book-author"] = ""
        create_review_data["book-publication_year"] = ""
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_missing_new_film(self, client: Client, create_review_data: dict):
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["film-title"] = ""
        create_review_data["film-director"] = ""
        create_review_data["film-release_year"] = ""
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_new_book_with_wrong_fields(self, client: Client, create_review_data: dict):
        # Submit data for new Film, even though Book was the selected content_type
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        film = FilmFactory.build()  # not saved to database
        create_review_data["film-title"] = film.title
        create_review_data["film-director"] = film.director
        create_review_data["film-release_year"] = film.release_year
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_new_film_with_wrong_fields(self, client: Client, create_review_data: dict):
        # Submit data for new Book, even though Film was the selected content_type
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        book = BookFactory.build()  # not saved to database
        create_review_data["book-title"] = book.title
        create_review_data["book-author"] = book.author
        create_review_data["book-publication_year"] = book.publication_year
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
