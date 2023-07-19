from typing import Any

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
    def _fake_get_content_type_id(self, model: Any) -> str:
        return {
            MaximusStrategy: "1",
            EbertStrategy: "2",
            GoodreadsStrategy: "3",
            Book: "4",
            Film: "5",
        }[model]

    def test_content_type_choices_applied(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "supergood_review_site.utils.Utils.get_content_type_id",
            self._fake_get_content_type_id,
        )
        review_form = ReviewForm(
            strategy_choices=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_type_choices=[Book, Film],
        )
        assert isinstance(review_form.fields["strategy_content_type"], ChoiceField)
        assert review_form.fields["strategy_content_type"].choices == [
            ("1", "Maximus"),
            ("2", "Ebert"),
            ("3", "Goodreads"),
        ]
        assert isinstance(review_form.fields["media_type_content_type"], ChoiceField)
        assert review_form.fields["media_type_content_type"].choices == [
            ("4", "Book"),
            ("5", "Film"),
        ]
