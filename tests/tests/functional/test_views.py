import json
from dataclasses import dataclass
from typing import Any, TypeAlias, cast
from urllib.parse import urlencode
from uuid import UUID, uuid4

import django
import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

from supergood_reads.models import Book, EbertStrategy, Film, GoodreadsStrategy, Review
from supergood_reads.reviews.forms import CreateNewMediaOption, ReviewForm
from supergood_reads.utils import ContentTypeUtils
from tests.factories import (
    BookFactory,
    EbertStrategyFactory,
    FilmFactory,
    GoodreadsStrategyFactory,
    MediaFormDataFactory,
    ReviewFactory,
    ReviewFormDataFactory,
    UserFactory,
)


@dataclass
class MediaTypeFixtureData:
    id: str
    title: str
    year: int


ReviewFormData: TypeAlias = dict[str, Any]


@pytest.fixture
def film_data() -> list[MediaTypeFixtureData]:
    return [
        MediaTypeFixtureData(
            id=data[0],
            title=data[1],
            year=data[2],
        )
        for data in [
            ("e01cdf31-c9d9-432e-a5b7-ac7a0049dd70", "Seven Samurai", 1954),
            ("794416b7-d07d-4651-80b6-64eadeea98b1", "Steel Magnolias", 1989),
            ("f99ba843-1ba8-4a1d-86c7-5edfd1722655", "Charade", 1963),
        ]
    ]


@pytest.fixture
def book_data() -> list[MediaTypeFixtureData]:
    return [
        MediaTypeFixtureData(
            id=data[0],
            title=data[1],
            year=data[2],
        )
        for data in [
            ("e01cdf31-c9d9-432e-a5b7-ac7a0049dd70", "Jane Eyre", 1847),
            ("794416b7-d07d-4651-80b6-64eadeea98b1", "The Age of Innocence", 1920),
            ("f99ba843-1ba8-4a1d-86c7-5edfd1722655", "Anna Karenina", 1878),
        ]
    ]


def media_type_response_matches(
    response: HttpResponse, expected: list[MediaTypeFixtureData]
) -> bool:
    """
    Compare just the "id" and "title" fields between json response and expected values.
    """
    fields_to_compare = ["id", "title"]
    actual = json.loads(response.content)["results"]

    if len(actual) != len(expected):
        return False

    for actual_item, expected_item in zip(actual, expected):
        for field in fields_to_compare:
            if actual_item[field] != getattr(expected_item, field):
                return False

    return True


@pytest.fixture
def reviewer_user(django_user_model: User) -> User:
    call_command("supergood_reads_create_groups")
    user = django_user_model.objects.create_user(  # noqa: S106
        username="valid_user", password="test"
    )
    reviewer_group = Group.objects.get(name="supergood_reads.Reviewer")
    user.groups.add(reviewer_group)
    return user


def is_redirected_to_login(res: Any) -> bool:
    """Check if response will redirect to login page."""
    res_url_root: str = res.url.split("?")[0]
    return res.status_code == 302 and res_url_root == settings.LOGIN_URL


def media_type_autocomplete_url(content_type_id: int | str) -> str:
    base_url = reverse("media_type_autocomplete")
    query_params = urlencode({"content_type_id": content_type_id})
    return f"{base_url}?{query_params}"


@pytest.mark.django_db
class TestMediaTypeAutocompleteView:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        book_content_type = ContentTypeUtils.get_content_type_id(Book)
        self.book_autocomplete_url = media_type_autocomplete_url(book_content_type)
        film_content_type = ContentTypeUtils.get_content_type_id(Film)
        self.film_autocomplete_url = media_type_autocomplete_url(film_content_type)

    def test_film_without_q(
        self, admin_client: Client, film_data: list[MediaTypeFixtureData]
    ) -> None:
        """Should return all films."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data.id),
                title=data.title,
                year=data.year,
            )
        url = self.film_autocomplete_url
        response = admin_client.get(url)
        assert response.status_code == 200
        assert media_type_response_matches(cast(HttpResponse, response), film_data)

    def test_film_with_q(
        self, admin_client: Client, film_data: list[MediaTypeFixtureData]
    ) -> None:
        """Should only return queried film."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data.id),
                title=data.title,
                year=data.year,
            )
        url = self.film_autocomplete_url
        response = admin_client.get(url + "&q=Charade")
        assert response.status_code == 200
        assert media_type_response_matches(cast(HttpResponse, response), [film_data[2]])

    def test_book_without_q(
        self, admin_client: Client, book_data: list[MediaTypeFixtureData]
    ) -> None:
        """Should return all films."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data.id),
                title=data.title,
                year=data.year,
            )
        url = self.book_autocomplete_url
        response = admin_client.get(url)
        assert response.status_code == 200
        assert media_type_response_matches(cast(HttpResponse, response), book_data)

    def test_book_with_q(
        self, admin_client: Client, book_data: list[MediaTypeFixtureData]
    ) -> None:
        """Should only return queried film."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data.id),
                title=data.title,
                year=data.year,
            )
        url = self.book_autocomplete_url
        response = admin_client.get(url + "&q=Anna")
        assert response.status_code == 200
        assert media_type_response_matches(cast(HttpResponse, response), [book_data[2]])


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

    def test_view_unauthenciated(self, client: Client, django_user_model: User) -> None:
        book = BookFactory()
        review = ReviewFactory.build(media_type=book, text="It was okay.")
        data = ReviewFormDataFactory(instance=review).data
        # Allow Views
        response = client.get(self.url)
        assert response.status_code == 200
        # Disallow Posts
        response = client.post(self.url, data)
        assert is_redirected_to_login(response)
        user = django_user_model.objects.create_user(  # noqa: S106
            username="valid_user", password="test"
        )
        add_perm = Permission.objects.get(
            codename="add_review", content_type__app_label="supergood_reads"
        )
        user.user_permissions.add(add_perm)
        client.force_login(user)
        # Allow Posts with proper Permission
        response = client.post(self.url, data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.text == "It was okay."

    def test_existing_book(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        book = BookFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["review-media_type_object_id"] = book.id
        response = client.post(self.url, create_review_data)
        assert is_redirected_to_login(response)
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type == book
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."
        assert review.owner == reviewer_user

    def test_existing_film(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        film = FilmFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["review-media_type_object_id"] = film.id
        response = client.post(self.url, create_review_data)
        assert is_redirected_to_login(response)
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type == film
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."
        assert review.owner == reviewer_user

    def test_non_existent_book(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory.build()
        book.owner.save()
        review = ReviewFactory.build(media_type=book)
        data = ReviewFormDataFactory(instance=review).data
        client.force_login(reviewer_user)
        # Should return error if media_type_object_id doesn't exist
        response = client.post(self.url, data, follow=True)
        assert response.status_code == 400
        res_form = cast(ReviewForm, response.context.get("review_form"))
        assert (
            res_form.errors["media_type_object_id"][0]
            == "The selected object does not exist."
        )
        # Should succeed once media_type is saved in db
        book.save()
        response = client.post(self.url, data, follow=True)
        assert response.status_code == 200

    def test_create_new_book(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        book = BookFactory.build()  # not saved to database
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["book-title"] = book.title
        create_review_data["book-author"] = book.author
        create_review_data["book-year"] = book.year
        response = client.post(self.url, create_review_data)
        assert is_redirected_to_login(response)
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type
        assert review.media_type.title == book.title
        assert review.media_type.owner == reviewer_user

    def test_create_new_film(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        film = FilmFactory.build()  # not saved to database
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["film-title"] = film.title
        create_review_data["film-director"] = film.director
        create_review_data["film-year"] = film.year
        response = client.post(self.url, create_review_data)
        assert is_redirected_to_login(response)
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type
        assert review.media_type.title == film.title
        assert review.media_type.owner == reviewer_user

    def test_missing_selected_book(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that book autocomplete field has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        autocomplete_tag = soup.find("autocomplete")
        assert "This field is required." in str(autocomplete_tag)

    def test_missing_selected_film(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0
        # Check that film autocomplete field has error message above it.
        soup = BeautifulSoup(response.content, "html.parser")
        autocomplete_tag = soup.find("autocomplete")
        assert "This field is required." in str(autocomplete_tag)

    def test_missing_new_book(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["book-title"] = ""
        create_review_data["book-author"] = ""
        create_review_data["book-year"] = ""
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_missing_new_film(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["film-title"] = ""
        create_review_data["film-director"] = ""
        create_review_data["film-year"] = ""
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_new_book_with_wrong_fields(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        # Submit data for new Film, even though Book was the selected content_type
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        film = FilmFactory.build()  # not saved to database
        create_review_data["film-title"] = film.title
        create_review_data["film-director"] = film.director
        create_review_data["film-year"] = film.year
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0

    def test_new_film_with_wrong_fields(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        # Submit data for new Book, even though Film was the selected content_type
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        book = BookFactory.build()  # not saved to database
        create_review_data["book-title"] = book.title
        create_review_data["book-author"] = book.author
        create_review_data["book-year"] = book.year
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0


@pytest.mark.django_db
class TestUpdateBookView:
    def get_url(self, book_id: UUID) -> str:
        return reverse("update_media_item", args=[book_id])

    def test_update_title(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = MediaFormDataFactory(instance=book).data
        data["book-title"] = new_title
        res = client.post(url, data)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 403
        book.owner = reviewer_user
        book.save()
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        book.refresh_from_db()
        assert book.title == new_title

    def test_missing_required_field(self, client: Client, reviewer_user: User) -> None:
        book_content_type_id = str(ContentTypeUtils.get_content_type_id(Book))
        book = BookFactory(owner=reviewer_user)
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = MediaFormDataFactory(instance=book).data
        data["book-title"] = new_title
        del data["book-author"]
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.context.get("media_type_forms_by_id")[book_content_type_id].errors["author"][0] == "This field is required."  # type: ignore[index]
        book.refresh_from_db()
        assert book.title != new_title

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "error"


@pytest.mark.django_db
class TestUpdateFilmView:
    def get_url(self, film_id: UUID) -> str:
        return reverse("update_media_item", args=[film_id])

    def test_update_title(self, client: Client, reviewer_user: User) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = MediaFormDataFactory(instance=film).data
        data["film-title"] = new_title
        res = client.post(url, data)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 403
        film.owner = reviewer_user
        film.save()
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        film.refresh_from_db()
        assert film.title == new_title

    def test_missing_required_field(self, client: Client, reviewer_user: User) -> None:
        film_content_type_id = str(ContentTypeUtils.get_content_type_id(Film))
        film = FilmFactory(owner=reviewer_user)
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = MediaFormDataFactory(instance=film).data
        data["film-title"] = new_title
        del data["film-director"]
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.context.get("media_type_forms_by_id")[film_content_type_id].errors["director"][0] == "This field is required."  # type: ignore[index]
        film.refresh_from_db()
        assert film.title != new_title

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "error"


@pytest.mark.django_db
class TestDeleteBook:
    def get_url(self, book_id: UUID) -> str:
        return reverse("delete_media_item", args=[book_id])

    def test_delete(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        res = client.post(url)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 403
        book.owner = reviewer_user
        book.save()
        res = client.post(url, follow=True)
        assert res.status_code == 200
        with pytest.raises(Book.DoesNotExist):
            book.refresh_from_db()

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 404

    def test_delete_reviews(self, client: Client, reviewer_user: User) -> None:
        another_user = UserFactory()
        book = BookFactory(owner=reviewer_user)
        review = ReviewFactory(media_type=book, owner=another_user)
        url = self.get_url(book.id)
        res = client.post(url)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)

        # Not allowed to delete as long as a Review exists that belongs to someone else.
        res = client.post(url)
        assert Book.objects.filter(pk=book.pk).exists()
        assert Review.objects.filter(pk=review.pk).exists()
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "error"

        # Reviews and Book will be deleted once all Reviews are owned by reviewer_user.
        review.owner = reviewer_user
        review.save()
        res = client.post(url)
        assert not Book.objects.filter(pk=book.pk).exists()
        assert not Review.objects.filter(pk=review.pk).exists()
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "success"


@pytest.mark.django_db
class TestDeleteFilm:
    def get_url(self, film_id: UUID) -> str:
        return reverse("delete_media_item", args=[film_id])

    def test_delete(self, client: Client, reviewer_user: User) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        res = client.post(url)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 403
        film.owner = reviewer_user
        film.save()
        res = client.post(url, follow=True)
        assert res.status_code == 200
        with pytest.raises(Film.DoesNotExist):
            film.refresh_from_db()

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 404

    def test_delete_reviews(self, client: Client, reviewer_user: User) -> None:
        another_user = UserFactory()
        film = FilmFactory(owner=reviewer_user)
        review = ReviewFactory(media_type=film, owner=another_user)
        url = self.get_url(film.id)
        res = client.post(url)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)

        # Not allowed to delete as long as a Review exists that belongs to someone else.
        res = client.post(url)
        assert Film.objects.filter(pk=film.pk).exists()
        assert Review.objects.filter(pk=review.pk).exists()
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "error"

        # Reviews and Film will be deleted once all Reviews are owned by reviewer_user.
        review.owner = reviewer_user
        review.save()
        res = client.post(url)
        assert not Film.objects.filter(pk=film.pk).exists()
        assert not Review.objects.filter(pk=review.pk).exists()
        messages = list(get_messages(res.wsgi_request))
        assert messages[-1].level_tag == "success"


@pytest.mark.django_db
class TestDeleteReviewView:
    def get_url(self, review_id: UUID) -> str:
        return reverse("delete_review", args=[review_id])

    def test_delete(self, admin_client: Client) -> None:
        review = ReviewFactory()
        url = self.get_url(review.id)
        res = admin_client.post(url)
        assert res.status_code == 302
        with pytest.raises(Review.DoesNotExist):
            review.refresh_from_db()

    def test_wrong_uuid(self, admin_client: Client) -> None:
        url = self.get_url(uuid4())
        res = admin_client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestUpdateReviewView:
    def get_url(self, review_id: UUID) -> str:
        return reverse("update_review", args=[review_id])

    def test_update_own_review(self, client: Client, reviewer_user: User) -> None:
        review = ReviewFactory(text="It was bad.", owner=reviewer_user)
        data = ReviewFormDataFactory(instance=review).data
        data["review-text"] = "It was good."
        url = self.get_url(review.id)
        res = client.post(url, data)
        assert is_redirected_to_login(res)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        assert review.text == "It was good."

    def test_update_other_review(self, client: Client, reviewer_user: User) -> None:
        original_user = UserFactory()
        review = ReviewFactory(text="It was bad.", owner=original_user)
        data = ReviewFormDataFactory(instance=review).data
        data["review-text"] = "It was good."
        # Unauthorized user can't update review
        url = self.get_url(review.id)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 403

        # Authorized user with permission, can update review
        change_perm = Permission.objects.get(
            codename="change_review", content_type__app_label="supergood_reads"
        )
        reviewer_user.user_permissions.add(change_perm)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        assert review.text == "It was good."
        assert review.owner == original_user

    def test_update_strategy(self, client: Client, reviewer_user: User) -> None:
        """Test that existing strategy is only updated and not replaced."""
        strategy = GoodreadsStrategyFactory(stars=5)
        review = ReviewFactory(strategy=strategy, owner=reviewer_user)
        data = ReviewFormDataFactory(instance=review).data
        data["goodreadsstrategy-stars"] = 4
        url = self.get_url(review.id)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        # In pre-4.2 versions of django, related fields are not automatically refreshed.
        if django.VERSION < (4, 2):
            review.strategy.refresh_from_db()
        assert review.strategy.id == strategy.id
        assert review.strategy.stars == 4

    def test_replace_strategy(self, client: Client, reviewer_user: User) -> None:
        """Test that existing strategy is replaced when we change strategies."""
        strategy = EbertStrategyFactory()
        review = ReviewFactory(strategy=strategy, owner=reviewer_user)
        data = ReviewFormDataFactory(instance=review).data
        data["review-strategy_content_type"] = ContentTypeUtils.get_content_type_id(
            GoodreadsStrategy
        )
        data["goodreadsstrategy-stars"] = 4
        url = self.get_url(review.id)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        assert review.strategy.stars == 4
        with pytest.raises(EbertStrategy.DoesNotExist):
            strategy.refresh_from_db()

    def test_view_demo(self, client: Client) -> None:
        review = ReviewFactory(demo=True)
        url = self.get_url(review.id)
        res = client.get(url)
        assert res.status_code == 200
        assert res.request["PATH_INFO"] == reverse(
            "update_review", kwargs={"pk": review.id}
        )

    def test_view_non_demo(self, client: Client, django_user_model: Any) -> None:
        # Unauthorized user can't see review
        review = ReviewFactory(demo=False)
        url = self.get_url(review.id)
        res = client.get(url)
        assert is_redirected_to_login(res)

        # Authorized user with permission can see review
        user: User = django_user_model.objects.create_user(  # noqa: S106
            username="user", password="test"
        )
        view_perm = Permission.objects.get(
            codename="view_review", content_type__app_label="supergood_reads"
        )
        user.user_permissions.add(view_perm)
        client.force_login(user)
        res = client.get(url, follow=True)
        assert res.status_code == 200
        assert res.request["PATH_INFO"] == reverse(
            "update_review", kwargs={"pk": review.id}
        )

    def test_view_own_review(self, client: Client, reviewer_user: User) -> None:
        review = ReviewFactory()
        url = self.get_url(review.id)
        client.force_login(reviewer_user)
        res = client.get(url, follow=True)
        assert res.status_code == 403
        review.owner = reviewer_user
        review.save()
        res = client.get(url, follow=True)
        assert res.status_code == 200
