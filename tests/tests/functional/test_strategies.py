from decimal import Decimal

import pytest

from supergood_review_site.strategies.ebert.forms import GREAT_FILM, EbertStrategyForm
from supergood_review_site.utils.forms import get_initial_field_value


@pytest.mark.django_db
class TestEbertStrategyForm:
    def test_great_film(self) -> None:
        form = EbertStrategyForm({"rating": GREAT_FILM})
        strategy = form.save()
        assert strategy.great_film is True
        assert strategy.stars == Decimal("4.0")

        update_form = EbertStrategyForm(instance=strategy)
        assert get_initial_field_value(update_form, "rating") == GREAT_FILM

    def test_star_rating(self) -> None:
        form = EbertStrategyForm({"rating": "3.5"})
        strategy = form.save()
        assert strategy.great_film is False
        assert strategy.stars == Decimal("3.5")

        update_form = EbertStrategyForm(instance=strategy)
        assert get_initial_field_value(update_form, "rating") == "3.5"

    def test_none(self) -> None:
        form = EbertStrategyForm({"rating": None})
        strategy = form.save()
        assert strategy.great_film is False
        assert strategy.stars is None

        update_form = EbertStrategyForm(instance=strategy)
        assert get_initial_field_value(update_form, "rating") is None

    def test_zero(self) -> None:
        form = EbertStrategyForm({"rating": "0.0"})
        strategy = form.save()
        assert strategy.great_film is False
        assert strategy.stars == Decimal("0.0")

        update_form = EbertStrategyForm(instance=strategy)
        assert get_initial_field_value(update_form, "rating") == "0.0"
