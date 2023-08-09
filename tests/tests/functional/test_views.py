import json
from typing import Any, TypeAlias, TypedDict, Union
from uuid import UUID, uuid4

import django
import pytest
from bs4 import BeautifulSoup, Tag
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from supergood_reads.models import Book, EbertStrategy, Film, GoodreadsStrategy, Review
from supergood_reads.reviews.forms import CreateNewMediaOption
from supergood_reads.utils import ContentTypeUtils
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


@pytest.fixture
def reviewer_user(django_user_model: User) -> User:
    call_command("create_groups")
    user = django_user_model.objects.create_user(  # noqa: S106
        username="valid_user", password="test"
    )
    reviewer_group = Group.objects.get(name="supergood_reads.Reviewer")
    user.groups.add(reviewer_group)
    return user


@pytest.mark.django_db
class TestFilmAutocompleteView:
    def test_without_q(self, admin_client: Client, film_data: FixtureData) -> None:
        """Should return all films."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                release_year=data["release_year"],
            )
        url = reverse("film_autocomplete")
        response = admin_client.get(url)
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], film_data)

    def test_with_q(self, admin_client: Client, film_data: FixtureData) -> None:
        """Should only return queried film."""
        for data in film_data:
            FilmFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                release_year=data["release_year"],
            )
        url = reverse("film_autocomplete")
        response = admin_client.get(url, {"q": "Charade"})
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], [film_data[2]])


@pytest.mark.django_db
class TestBookAutocompleteView:
    def test_without_q(self, admin_client: Client, book_data: FixtureData) -> None:
        """Should return all films."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                publication_year=data["publication_year"],
            )
        url = reverse("book_autocomplete")
        response = admin_client.get(url)
        assert response.status_code == 200
        assert cmp(json.loads(response.content)["results"], book_data)

    def test_with_q(self, admin_client: Client, book_data: FixtureData) -> None:
        """Should only return queried film."""
        for data in book_data:
            BookFactory.create(
                id=UUID(data["id"]),
                title=data["title"],
                publication_year=data["publication_year"],
            )
        url = reverse("book_autocomplete")
        response = admin_client.get(url, {"q": "Anna"})
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

    def test_view_unauthenciated(self, client: Client, django_user_model: User) -> None:
        book = BookFactory()
        review = ReviewFactory.build(media_type=book, text="It was okay.")
        data = ReviewFormDataFactory(instance=review).data
        # Allow Views
        response = client.get(self.url)
        assert response.status_code == 200
        # Disallow Posts
        response = client.post(self.url, data, follow=True)
        assert response.status_code == 401
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
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 401
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type == book
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_existing_film(
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        film = FilmFactory.create()
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.SELECT_EXISTING.value
        create_review_data["review-media_type_content_type"] = self.film_content_type
        create_review_data["review-media_type_object_id"] = film.id
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 401
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type == film
        assert review.strategy
        assert review.strategy.stars == 5
        assert review.text == "It was good."

    def test_non_existent_book(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory.build()
        book.owner.save()
        review = ReviewFactory.build(media_type=book)
        data = ReviewFormDataFactory(instance=review).data
        client.force_login(reviewer_user)
        # Should return error if media_type_object_id doesn't exist
        response = client.post(self.url, data, follow=True)
        assert response.status_code == 400
        assert (
            response.context.get("review_form").errors["media_type_object_id"][0]
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
        create_review_data["book-publication_year"] = book.publication_year
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 401
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type
        assert review.media_type.title == book.title

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
        create_review_data["film-release_year"] = film.release_year
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 401
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data, follow=True)
        assert response.status_code == 200
        review = Review.objects.first()
        assert review
        assert review.media_type
        assert review.media_type.title == film.title

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
        self, client: Client, create_review_data: ReviewFormData, reviewer_user: User
    ) -> None:
        create_review_data[
            "review_mgmt-create_new_media_type_object"
        ] = CreateNewMediaOption.CREATE_NEW.value
        create_review_data["review-media_type_content_type"] = self.book_content_type
        create_review_data["book-title"] = ""
        create_review_data["book-author"] = ""
        create_review_data["book-publication_year"] = ""
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
        create_review_data["film-release_year"] = ""
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
        create_review_data["film-release_year"] = film.release_year
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
        create_review_data["book-publication_year"] = book.publication_year
        client.force_login(reviewer_user)
        response = client.post(self.url, create_review_data)
        assert response.status_code == 400
        assert Review.objects.count() == 0


@pytest.mark.django_db
class TestUpdateMyMediaBookView:
    def get_url(self, book_id: UUID) -> str:
        return reverse("update_book", args=[book_id])

    def test_update_title(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
            "author": book.author,
            "publication_year": book.publication_year,
        }
        res = client.post(url, data)
        assert res.status_code == 403
        client.force_login(reviewer_user)
        res = client.post(url, data)
        book.owner = reviewer_user
        book.save()
        assert res.status_code == 403
        res = client.post(url, data)
        assert res.status_code == 200
        assert res.json()["data"] == {
            "id": str(book.id),
            **data,
        }
        book.refresh_from_db()
        assert book.title == new_title

    def test_missing_required_field(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory(owner=reviewer_user)
        url = self.get_url(book.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
        }
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.json()["fieldErrors"]["author"][0] == "This field is required."
        book.refresh_from_db()
        assert book.title != new_title

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestUpdateMyMediaFilmView:
    def get_url(self, film_id: UUID) -> str:
        return reverse("update_film", args=[film_id])

    def test_update_title(self, client: Client, reviewer_user: User) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
            "director": film.director,
            "release_year": film.release_year,
        }
        res = client.post(url, data)
        assert res.status_code == 403
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 403
        film.owner = reviewer_user
        film.save()
        res = client.post(url, data)
        assert res.status_code == 200
        assert res.json()["data"] == {
            "id": str(film.id),
            **data,
        }
        film.refresh_from_db()
        assert film.title == new_title

    def test_missing_required_field(self, client: Client, reviewer_user: User) -> None:
        film = FilmFactory(owner=reviewer_user)
        url = self.get_url(film.id)
        new_title = "This is a new title"
        data = {
            "title": new_title,
        }
        client.force_login(reviewer_user)
        res = client.post(url, data)
        assert res.status_code == 400
        assert res.json()["fieldErrors"]["director"][0] == "This field is required."
        film.refresh_from_db()
        assert film.title != new_title

    def test_wrong_uuid(self, client: Client, reviewer_user: User) -> None:
        url = self.get_url(uuid4())
        client.force_login(reviewer_user)
        res = client.post(url)
        assert res.status_code == 404


@pytest.mark.django_db
class TestDeleteMyMediaBookView:
    def get_url(self, book_id: UUID) -> str:
        return reverse("delete_book", args=[book_id])

    def test_delete(self, client: Client, reviewer_user: User) -> None:
        book = BookFactory()
        url = self.get_url(book.id)
        res = client.post(url)
        assert res.status_code == 403
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


@pytest.mark.django_db
class TestDeleteMyMediaFilmView:
    def get_url(self, film_id: UUID) -> str:
        return reverse("delete_film", args=[film_id])

    def test_delete(self, client: Client, reviewer_user: User) -> None:
        film = FilmFactory()
        url = self.get_url(film.id)
        res = client.post(url)
        assert res.status_code == 403
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
        res = client.post(url, data, follow=True)
        assert res.status_code == 401
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        assert review.text == "It was good."

    def test_update_other_review(self, client: Client, reviewer_user: User) -> None:
        review = ReviewFactory(text="It was bad.")
        data = ReviewFormDataFactory(instance=review).data
        data["review-text"] = "It was good."
        # Unauthorized user can't update review
        url = self.get_url(review.id)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 403

        # Authorized user with permission, but non-staff, can't update review
        change_perm = Permission.objects.get(
            codename="change_review", content_type__app_label="supergood_reads"
        )
        reviewer_user.user_permissions.add(change_perm)
        client.force_login(reviewer_user)
        res = client.post(url, data, follow=True)
        assert res.status_code == 403

        # Authorized user with permission, and staff status, can update review
        reviewer_user.is_staff = True
        reviewer_user.save()
        res = client.post(url, data, follow=True)
        assert res.status_code == 200
        review.refresh_from_db()
        assert review.text == "It was good."

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

    def test_view_demo(self, client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
        review = ReviewFactory()
        url = self.get_url(review.id)
        res = client.get(url, follow=True)
        assert res.status_code == 401
        monkeypatch.setattr(
            "supergood_reads.utils.engine.supergood_reads_engine.config.demo_review_queryset",
            lambda: Review.objects.filter(id=review.id),
        )
        res = client.get(url, follow=True)
        assert res.status_code == 200

    def test_view_non_demo(self, client: Client, django_user_model: Any) -> None:
        # Unauthorized user can't see review
        review = ReviewFactory()
        url = self.get_url(review.id)
        res = client.get(url, follow=True)
        assert res.status_code == 401

        # Authorized user with permission, but non-staff, can't see review
        user: User = django_user_model.objects.create_user(  # noqa: S106
            username="user", password="test"
        )
        view_perm = Permission.objects.get(
            codename="view_review", content_type__app_label="supergood_reads"
        )
        user.user_permissions.add(view_perm)
        client.force_login(user)
        res = client.get(url, follow=True)
        assert res.status_code == 403

        # Authorized user with permission, and staff status, can see review
        user.is_staff = True
        user.save()
        res = client.get(url, follow=True)
        assert res.status_code == 200

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
