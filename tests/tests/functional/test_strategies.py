from decimal import Decimal

import pytest

from supergood_reads.forms.strategy_forms import GOAT, EbertStrategyForm


@pytest.mark.django_db
class TestEbertStrategyForm:
    def test_goat(self) -> None:
        form = EbertStrategyForm({"rating": GOAT})
        strategy = form.save()
        assert strategy.goat is True
        assert strategy.stars == Decimal("4.0")

        update_form = EbertStrategyForm(instance=strategy)
        assert update_form["rating"].value() == GOAT

    def test_star_rating(self) -> None:
        form = EbertStrategyForm({"rating": "3.5"})
        strategy = form.save()
        assert strategy.goat is False
        assert strategy.stars == Decimal("3.5")

        update_form = EbertStrategyForm(instance=strategy)
        assert update_form["rating"].value() == "3.5"

    def test_none(self) -> None:
        form = EbertStrategyForm({"rating": None})
        strategy = form.save()
        assert strategy.goat is False
        assert strategy.stars is None

        update_form = EbertStrategyForm(instance=strategy)
        assert update_form["rating"].value() is None

    def test_zero(self) -> None:
        form = EbertStrategyForm({"rating": "0.0"})
        strategy = form.save()
        assert strategy.goat is False
        assert strategy.stars == Decimal("0.0")

        update_form = EbertStrategyForm(instance=strategy)
        assert update_form["rating"].value() == "0.0"
