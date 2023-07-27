import json
from typing import Any, TypeAlias, TypedDict, Union
from uuid import UUID, uuid4

import pytest
from bs4 import BeautifulSoup, Tag
from django.test import Client
from django.urls import reverse

from supergood_review_site.models import (
    Book,
    EbertStrategy,
    Film,
    GoodreadsStrategy,
    Review,
)
from supergood_review_site.reviews.forms import CreateNewMediaOption
from supergood_review_site.utils import ContentTypeUtils
from tests.factories import (
    BookFactory,
    EbertStrategyFactory,
    FilmFactory,
    GoodreadsStrategyFactory,
    ReviewFactory,
    ReviewFormDataFactory,
)


class FixtureDataItem(TypedDict, total=False):
    id: str
    title: str
    release_year: int
    publication_year: int


FixtureData: TypeAlias = list[FixtureDataItem]

ReviewFormData: TypeAlias = dict[str, Any]


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
    def setup(self) -> None:
        self.url = reverse("create_review")
        self.book_content_type = ContentTypeUtils.get_content_type_id(Book)
        self.film_content_type = ContentTypeUtils.get_content_type_id(Film)

    @pytest.fixture
    def create_review_data(self) -> ReviewFormData:
        """dict(request.POST.items()) from CreateReviewView.post"""
        data = ReviewFormDataFactory().data
        data["review-strategy_content_type"] = ContentTypeUtils.get_content_type_id(
            GoodreadsStrategy
        )
        data["goodreadsstrategy-stars"] = "5"
        data["review-text"] = "It was good."
        return data

    def test_existing_book(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
        book = BookFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["review-media_type_object_id"] = book.id
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review
        assert review.media_type == book
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_existing_film(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
        film = FilmFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["review-media_type_object_id"] = film.id
        response = client.post(self.url, create_review_data)
        assert response.status_code == 302
        review = Review.objects.first()
        assert review
        assert review.media_type == film
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_create_new_book(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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
        assert review
        assert review.media_type
        assert review.media_type.title == book.title

    def test_create_new_film(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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
        assert review
        assert review.media_type
        assert review.media_type.title == film.title

    def test_missing_selected_book(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that book autocomplete field has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        assert (
            autocomplete_tag := soup.find(
                "autocomplete", attrs={"url": "/app/book-autocomplete/"}
            )
        )
        assert (parent_tag := autocomplete_tag.parent)
        assert (error_list_tag := parent_tag.find("ul", attrs={"class": "errorlist"}))
        assert isinstance((error_list_item_tag := error_list_tag.find("li")), Tag)
        assert error_list_item_tag.text == "This field is required."

    def test_missing_selected_film(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that film autocomplete field has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        assert (
            autocomplete_tag := soup.find(
                "autocomplete", attrs={"url": "/app/film-autocomplete/"}
            )
        )
        assert (parent_tag := autocomplete_tag.parent)
        assert (error_list_tag := parent_tag.find("ul", attrs={"class": "errorlist"}))
        assert isinstance((error_list_item_tag := error_list_tag.find("li")), Tag)
        assert error_list_item_tag.text == "This field is required."

    def test_missing_new_book(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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

    def test_missing_new_film(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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

    def test_new_book_with_wrong_fields(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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

    def test_new_film_with_wrong_fields(
        self, client: Client, create_review_data: ReviewFormData
    ) -> None:
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


@pytest.mark.django_db
class TestUpdateMyMediaBookView:
    def get_url(self, book_id: UUID) -> str:
        return reverse("update_book", args=[book_id])

    def test_update_title(self, client: Client) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
            "author": book.author,
            "publication_year": book.publication_year,
        }
        res = client.post(url, data)
        assert res.status_code == 200
        assert res.json()["data"] == {
            "id": str(book.id),
            **data,
        }
        book.refresh_from_db()
        assert book.title == new_title

    def test_missing_required_field(self, client: Client) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
        }
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.json()["errors"]["author"][0] == "This field is required."
        book.refresh_from_db()
        assert book.title != new_title

    def test_wrong_uuid(self, client: Client) -> None:
        url = self.get_url(uuid4())
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestUpdateMyMediaFilmView:
    def get_url(self, film_id: UUID) -> str:
        return reverse("update_film", args=[film_id])

    def test_update_title(self, client: Client) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
            "director": film.director,
            "release_year": film.release_year,
        }
        res = client.post(url, data)
        assert res.status_code == 200
        assert res.json()["data"] == {
            "id": str(film.id),
            **data,
        }
        film.refresh_from_db()
        assert film.title == new_title

    def test_missing_required_field(self, client: Client) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
        }
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.json()["errors"]["director"][0] == "This field is required."
        film.refresh_from_db()
        assert film.title != new_title

    def test_wrong_uuid(self, client: Client) -> None:
        url = self.get_url(uuid4())
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestDeleteMyMediaBookView:
    def get_url(self, book_id: UUID) -> str:
        return reverse("delete_book", args=[book_id])

    def test_delete(self, client: Client) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        res = client.post(url)
        assert res.status_code == 302
        with pytest.raises(Book.DoesNotExist):
            book.refresh_from_db()

    def test_wrong_uuid(self, client: Client) -> None:
        url = self.get_url(uuid4())
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestDeleteMyMediaFilmView:
    def get_url(self, film_id: UUID) -> str:
        return reverse("delete_film", args=[film_id])

    def test_delete(self, client: Client) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        res = client.post(url)
        assert res.status_code == 302
        with pytest.raises(Film.DoesNotExist):
            film.refresh_from_db()

    def test_wrong_uuid(self, client: Client) -> None:
        url = self.get_url(uuid4())
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestDeleteReviewView:
    def get_url(self, review_id: UUID) -> str:
        return reverse("delete_review", args=[review_id])

    def test_delete(self, client: Client) -> None:
        review = ReviewFactory()
        url = self.get_url(review.id)
        res = client.post(url)
        assert res.status_code == 302
        with pytest.raises(Review.DoesNotExist):
            review.refresh_from_db()

    def test_wrong_uuid(self, client: Client) -> None:
        url = self.get_url(uuid4())
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestUpdateReviewView:
    def get_url(self, review_id: UUID) -> str:
        return reverse("update_review", args=[review_id])

    @pytest.fixture
    def update_review_data(self, review_form_data: ReviewFormData) -> ReviewFormData:
        """dict(request.POST.items()) from CreateReviewView.post"""
        data = review_form_data
        data["review-strategy_content_type"] = ContentTypeUtils.get_content_type_id(
            GoodreadsStrategy
        )
        data["goodreadsstrategy-stars"] = "5"
        data["review-text"] = "It was good."
        return data

    def test_update(self, client: Client) -> None:
        review = ReviewFactory(text="It was bad.")
        data = ReviewFormDataFactory(instance=review).data
        data["review-text"] = "It was good."
        url = self.get_url(review.id)
        res = client.post(url, data)
        assert res.status_code == 302
        review.refresh_from_db()
        assert review.text == "It was good."

    def test_update_strategy(self, client: Client) -> None:
        """Test that existing strategy is only updated and not replaced."""
        strategy = GoodreadsStrategyFactory(stars=5)
        review = ReviewFactory(strategy=strategy)
        data = ReviewFormDataFactory(instance=review).data
        data["goodreadsstrategy-stars"] = 4
        url = self.get_url(review.id)
        res = client.post(url, data)
        assert res.status_code == 302
        review.refresh_from_db()
        assert review.strategy.id == strategy.id
        assert review.strategy.stars == 4

    def test_replace_strategy(self, client: Client) -> None:
        """Test that existing strategy is replaced when we change strategies."""
        strategy = EbertStrategyFactory()
        review = ReviewFactory(strategy=strategy)
        data = ReviewFormDataFactory(instance=review).data
        data["review-strategy_content_type"] = ContentTypeUtils.get_content_type_id(
            GoodreadsStrategy
        )
        data["goodreadsstrategy-stars"] = 4
        url = self.get_url(review.id)
        res = client.post(url, data)
        assert res.status_code == 302
        review.refresh_from_db()
        assert review.strategy.stars == 4
        with pytest.raises(EbertStrategy.DoesNotExist):
            strategy.refresh_from_db()
