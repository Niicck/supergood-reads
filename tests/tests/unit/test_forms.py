import pytest
from django.forms.fields import ChoiceField

from supergood_review_site.media_types.models import Book, Film
from supergood_review_site.reviews.forms import ReviewForm
from supergood_review_site.strategies.models import (
    EbertStrategy,
    GoodreadsStrategy,
    MaximusStrategy,
)


class TestReviewForm:
    def test_content_type_choices_default(self) -> None:
        review_form = ReviewForm()
        assert isinstance(review_form.fields["strategy_content_type"], ChoiceField)
        assert not review_form.fields["strategy_content_type"].choices
        assert isinstance(review_form.fields["media_type_content_type"], ChoiceField)
        assert not review_form.fields["media_type_content_type"].choices

    def test_content_type_choices_applied(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "supergood_review_site.utils.Utils.get_content_type_id", lambda _: 1
        )
        review_form = ReviewForm(
            strategies=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_types=[Book, Film],
        )
        assert isinstance(review_form.fields["strategy_content_type"], ChoiceField)
        assert review_form.fields["strategy_content_type"].choices == [
            ("1", "Maximus"),
            ("1", "Ebert"),
            ("1", "Goodreads"),
        ]
        assert isinstance(review_form.fields["media_type_content_type"], ChoiceField)
        assert review_form.fields["media_type_content_type"].choices == [
            ("1", "Book"),
            ("1", "Film"),
        ]
