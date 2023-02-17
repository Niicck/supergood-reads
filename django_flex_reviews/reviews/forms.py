from typing import Any

from django import forms
from django.forms import ModelForm

import django_flex_reviews.strategies.models as strategy_models
from django_flex_reviews.reviews.models import Review

strategy_forms = [
    strategy_models.EbertStrategy,
    strategy_models.GoodreadsStrategy,
    strategy_models.ImdbStrategy,
    strategy_models.LetterboxdStrategy,
    strategy_models.MaximusStrategy,
]


class ReviewForm(ModelForm[Review]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        pass

    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "strategy",
        ]

    strategy = forms.ChoiceField(
        choices=(
            (strategy._meta.verbose_name, strategy._meta.verbose_name)
            for strategy in strategy_forms
        )
    )
