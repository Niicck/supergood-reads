from typing import Any

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

import django_flex_reviews.strategies.models as strategy_models
from django_flex_reviews.reviews.models import Review

eligible_strategy_models = [
    strategy_models.EbertStrategy,
    strategy_models.GoodreadsStrategy,
    strategy_models.MaximusStrategy,
]


class ReviewForm(ModelForm[Review]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "strategy_content_type",
        ]

    strategy_content_type = forms.ChoiceField(
        choices=(
            (
                ContentType.objects.get_for_model(strategy_model).id,
                strategy_model._meta.verbose_name,
            )
            for strategy_model in eligible_strategy_models
        ),
        label="Strategy",
    )
