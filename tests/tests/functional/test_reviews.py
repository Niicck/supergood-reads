import pytest
from django.core.exceptions import ValidationError

from supergood_review_site.reviews.models import Review
from tests.factories import ReviewFactory


@pytest.mark.django_db
class TestCompletedAt:
    def test_valid_date(self) -> None:
        r: Review = ReviewFactory(
            completed_at_day=2,
            completed_at_month=2,
            completed_at_year=2002,
        )
        assert r

    def test_invalid_date(self) -> None:
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=31,
                completed_at_month=2,
                completed_at_year=2002,
            )
        assert "{'completed_at_day': ['Invalid date.']}" in str(e)

    def test_missing_month_and_year(self) -> None:
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=2,
            )
        assert (
            "'completed_at_day': [\"Can't input a day without month and year.\"]"
            in str(e)
        )

    def test_missing_year(self) -> None:
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=31,
                completed_at_month=2,
            )
        assert "'completed_at_month': [\"Can't input a month without a year.\"]" in str(
            e
        )

    def test_missing_day_and_year(self) -> None:
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_month=2,
            )
        assert "'completed_at_month': [\"Can't input a month without a year.\"]" in str(
            e
        )
