from tests.factories import ReviewFactory


class TestReviewCompletedAt:
    def test_complete(self) -> None:
        review = ReviewFactory.build(
            completed_at_day="1",
            completed_at_month="1",
            completed_at_year="1999",
        )
        assert review.completed_at == "01 Jan 1999"

    def test_missing_day(self) -> None:
        review = ReviewFactory.build(
            completed_at_day=None,
            completed_at_month="1",
            completed_at_year="1999",
        )
        assert review.completed_at == "Jan 1999"

    def test_missing_day_and_month(self) -> None:
        review = ReviewFactory.build(
            completed_at_day=None,
            completed_at_month=None,
            completed_at_year="1999",
        )
        assert review.completed_at == "1999"

    def test_missing_all(self) -> None:
        review = ReviewFactory.build(
            completed_at_day=None,
            completed_at_month=None,
            completed_at_year=None,
        )
        assert review.completed_at == ""
