from typing import Any, Dict

import pytest

from supergood_review_site.media_types.models import Book, Film
from supergood_review_site.reviews.forms import ReviewForm
from supergood_review_site.strategies.models import (
    EbertStrategy,
    GoodreadsStrategy,
    MaximusStrategy,
)
from supergood_review_site.utils import ContentTypeUtils


@pytest.mark.django_db
class TestReviewForm:
    @pytest.fixture
    def form_data(self) -> Dict[str, Any]:
        return {
            "completed_at_day": "",
            "completed_at_month": "",
            "completed_at_year": "",
            "text": "It was good.",
            "media_type_content_type": ContentTypeUtils.get_content_type_id(Book),
            "media_type_object_id": "",
            "strategy_content_type": ContentTypeUtils.get_content_type_id(
                EbertStrategy
            ),
        }

    def test_valid_strategy_content_type(self, form_data: Dict[str, Any]) -> None:
        valid_content_type_id = ContentTypeUtils.get_content_type_id(MaximusStrategy)
        form_data["strategy_content_type"] = valid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_type_choices=[Book, Film],
        )
        assert form.is_valid()

    def test_invalid_strategy_content_type(self, form_data: Dict[str, Any]) -> None:
        invalid_content_type_id = ContentTypeUtils.get_content_type_id(Book)
        form_data["strategy_content_type"] = invalid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[Book],
            media_type_choices=[Book, Film],
        )
        assert not form.is_valid()
        assert (
            form.errors["strategy_content_type"][0]
            == f"{invalid_content_type_id} is not a valid AbstractStrategy."
        )

    def test_valid_media_type_content_type(self, form_data: Dict[str, Any]) -> None:
        valid_content_type_id = ContentTypeUtils.get_content_type_id(Book)
        form_data["media_type_content_type"] = valid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_type_choices=[Book, Film],
        )
        assert form.is_valid()

    def test_invalid_media_type_content_type(self, form_data: Dict[str, Any]) -> None:
        invalid_content_type_id = ContentTypeUtils.get_content_type_id(EbertStrategy)
        form_data["media_type_content_type"] = invalid_content_type_id
        form = ReviewForm(
            form_data,
            strategy_choices=[MaximusStrategy, EbertStrategy, GoodreadsStrategy],
            media_type_choices=[EbertStrategy],
        )
        assert not form.is_valid()
        assert (
            form.errors["media_type_content_type"][0]
            == f"{invalid_content_type_id} is not a valid AbstractMediaType."
        )


@pytest.mark.django_db
class TestReviewFormGroup:
    def test_update_review(self) -> None:
        raise NotImplementedError
