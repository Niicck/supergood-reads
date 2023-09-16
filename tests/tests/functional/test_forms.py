from typing import Any, Dict

import pytest

from supergood_reads.forms.review_forms import ReviewForm
from supergood_reads.models import (
    Book,
    EbertStrategy,
    Film,
    GoodreadsStrategy,
    TomatoStrategy,
)
from supergood_reads.utils.content_type import model_to_content_type_id


@pytest.mark.django_db
class TestReviewForm:
    @pytest.fixture
    def form_data(self) -> Dict[str, Any]:
        return {
            "completed_at_day": "",
            "completed_at_month": "",
            "completed_at_year": "",
            "text": "It was good.",
            "media_item_content_type": model_to_content_type_id(Book),
            "media_item_object_id": "",
            "strategy_content_type": model_to_content_type_id(EbertStrategy),
        }

    def test_valid_strategy_content_type(self, form_data: Dict[str, Any]) -> None:
        valid_content_type_id = model_to_content_type_id(TomatoStrategy)
        form_data["strategy_content_type"] = valid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[TomatoStrategy, EbertStrategy, GoodreadsStrategy],
            media_item_choices=[Book, Film],
        )
        assert form.is_valid()

    def test_invalid_strategy_content_type(self, form_data: Dict[str, Any]) -> None:
        invalid_content_type_id = model_to_content_type_id(Book)
        form_data["strategy_content_type"] = invalid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[Book],  # type: ignore[list-item]
            media_item_choices=[Book, Film],
        )
        assert not form.is_valid()
        assert (
            form.errors["strategy_content_type"][0]
            == "Book is not a valid AbstractReviewStrategy."
        )

    def test_valid_media_item(self, form_data: Dict[str, Any]) -> None:
        valid_content_type_id = model_to_content_type_id(Book)
        form_data["media_item_content_type"] = valid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[TomatoStrategy, EbertStrategy, GoodreadsStrategy],
            media_item_choices=[Book, Film],
        )
        assert form.is_valid()

    def test_invalid_media_item(self, form_data: Dict[str, Any]) -> None:
        invalid_content_type_id = model_to_content_type_id(EbertStrategy)
        form_data["media_item_content_type"] = invalid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[TomatoStrategy, EbertStrategy, GoodreadsStrategy],
            media_item_choices=[EbertStrategy],  # type: ignore[list-item]
        )
        assert not form.is_valid()
        assert (
            form.errors["media_item_content_type"][0]
            == "Ebert is not a valid BaseMediaItem."
        )
