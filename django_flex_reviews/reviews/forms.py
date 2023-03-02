from typing import Any, List, Optional, Type

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.forms.fields import ChoiceField

from django_flex_reviews.reviews.models import Review
from django_flex_reviews.strategies.base.models import AbstractStrategy


class ReviewForm(ModelForm[Review]):
    def __init__(
        self,
        *args: Any,
        strategies: Optional[List[Type[AbstractStrategy]]] = None,
        **kwargs: Any
    ) -> None:
        """
        Kwargs:
          strategies: list of strategy models to be used in strategy_content_type
            dropdown field
        """
        self.strategies = strategies or []
        super().__init__(*args, **kwargs)
        self.set_strategy_content_type_choices()

    def set_strategy_content_type_choices(self) -> None:
        """Plug in self.strategy_models into strategy_content_type field choices."""
        strategy_content_type_field = self.fields["strategy_content_type"]
        assert type(strategy_content_type_field) is ChoiceField
        strategy_content_type_field.choices = (
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

    strategy_content_type = forms.ChoiceField(label="Strategy", choices=[])
