import pytest
from django.core.exceptions import ValidationError

from tests.factories import ReviewFactory


@pytest.mark.django_db
class TestCompletedAt:
    def test_valid_date(self):
        r = ReviewFactory(
            completed_at_day=2,
            completed_at_month=2,
            completed_at_year=2002,
        )
        assert r

    def test_missing_day(self):
        r = ReviewFactory(
            completed_at_month=2,
            completed_at_year=2002,
        )
        assert r
        assert r.completed_at_day is None

    def test_missing_day_and_month(self):
        r = ReviewFactory(
            completed_at_year=2002,
        )
        assert r
        assert r.completed_at_day is None
        assert r.completed_at_month is None

    def test_missing_all(self):
        r = ReviewFactory(
            completed_at_day=None,
            completed_at_month=None,
            completed_at_year=None,
        )
        assert r
        assert r.completed_at_day is None
        assert r.completed_at_month is None
        assert r.completed_at_year is None

    def test_invalid_date(self):
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=31,
                completed_at_month=2,
                completed_at_year=2002,
            )
        assert "{'completed_at_day': ['Invalid date.']}" in str(e)

    def test_missing_month_and_year(self):
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=2,
            )
        assert (
            "'completed_at_day': [\"Can't input a day without a month or year.\"]"
            in str(e)
        )

    def test_missing_year(self):
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_day=31,
                completed_at_month=2,
            )
        assert "'completed_at_day': [\"Can't input a day without a year.\"]" in str(e)
        assert "'completed_at_month': [\"Can't input a month without a year.\"]" in str(
            e
        )

    def test_missing_day_and_year(self):
        with pytest.raises(ValidationError) as e:
            ReviewFactory(
                completed_at_month=2,
            )
        assert "'completed_at_month': [\"Can't input a month without a year.\"]" in str(
            e
        )
