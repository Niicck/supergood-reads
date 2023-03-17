import json
from typing import TypeAlias, TypedDict
from uuid import UUID

import pytest
from django.http import JsonResponse
from django.test import Client
from django.urls import reverse

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


def cmp(actual: JsonResponse, expected: list[FixtureData]):
    """Compare just the "id" and "title" fields between two dictionaries."""

    def filter(d):
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
