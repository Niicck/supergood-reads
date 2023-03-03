import pytest

from django_flex_reviews.media_types.models import Book, Film
from django_flex_reviews.reviews.forms import ReviewForm
from django_flex_reviews.strategies.models import (
    EbertStrategy,
    GoodreadsStrategy,
    MaximusStrategy,
)


class TestReviewForm:
    def test_content_type_choices_default(self):
        review_form = ReviewForm()
        assert not review_form.fields["strategy_content_type"].choices
        assert not review_form.fields["media_type_content_type"].choices

    def test_content_type_choices_applied(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "django_flex_reviews.utils.Utils.get_content_type_id", lambda _: 1
        )
        review_form = ReviewForm(
            strategies=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_types=[Book, Film],
        )
        assert review_form.fields["strategy_content_type"].choices == [
            (1, "Maximus"),
            (1, "Ebert"),
            (1, "Goodreads"),
        ]
        assert review_form.fields["media_type_content_type"].choices == [
            (1, "Book"),
            (1, "Film"),
        ]
