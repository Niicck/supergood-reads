from typing import Any, List, Type

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

from django_flex_reviews.reviews.models import Review
from django_flex_reviews.strategies.base.models import AbstractStrategy


class ReviewForm(ModelForm[Review]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Kawrgs:
          strategies: list of strategy models to be used in strategy_content_type
            dropdown field
        """
        self.strategies: List[Type[AbstractStrategy]] = []
        if "strategies" in kwargs:
            self.strategies = kwargs.get("strategies")
            kwargs.pop("strategies")

        super().__init__(*args, **kwargs)
        self.set_strategy_content_type_choices()

    def set_strategy_content_type_choices(self) -> None:
        """Plug in self.strategy_models into strategy_content_type field choices."""
        self.fields["strategy_content_type"].choices = (
            (
                ContentType.objects.get_for_model(strategy_model).id,
                strategy_model._meta.verbose_name,
            )
            for strategy_model in self.strategies
        )

    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "strategy_content_type",
        ]

    strategy_content_type = forms.ChoiceField(label="Strategy")
