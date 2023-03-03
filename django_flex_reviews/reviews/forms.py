from typing import Any, List, Optional, Type

from django import forms
from django.db import models
from django.forms import ModelForm
from django.forms.fields import ChoiceField

from django_flex_reviews.media_types.models import AbstractMediaType
from django_flex_reviews.reviews.models import Review
from django_flex_reviews.strategies.base.models import AbstractStrategy
from django_flex_reviews.utils import Utils


class ReviewForm(ModelForm[Review]):
    def __init__(
        self,
        *args: Any,
        strategies: Optional[List[Type[AbstractStrategy]]] = None,
        media_types: Optional[List[Type[AbstractMediaType]]] = None,
        **kwargs: Any
    ) -> None:
        """
        Kwargs:
          strategies:
            list of strategy models to be used in strategy_content_type dropdown field
          media_types:
            list of media_type models to be used in media_type_content_type dropdown field
        """
        self.strategies = strategies or []
        self.media_types = media_types or []
        super().__init__(*args, **kwargs)
        self.add_models_to_content_type_field("strategy_content_type", self.strategies)
        self.add_models_to_content_type_field(
            "media_type_content_type", self.media_types
        )

    def add_models_to_content_type_field(
        self, content_type_field_name: str, models: List[Type[models.Model]]
    ):
        """Plug in models' content_type_ids into ChoiceField for a ContentType relation.

        Args:
          content_type_field_name:
            Name of the ChoiceField to add choices to. This should be a ForeignKey to
            the ContentType table.
          models:
            List of models that can be selected from the content_type_field
        """
        content_type_field = self.fields[content_type_field_name]
        assert type(content_type_field) is ChoiceField
        content_type_field.choices = []
        for model in models:
            model_content_type_id = Utils.get_content_type_id(model)
            model_name = model._meta.verbose_name
            choice = (model_content_type_id, model_name)
            content_type_field.choices.append(choice)

    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "strategy_content_type",
            "media_type_content_type",
        ]
        labels = {
            "text": "Review",
        }

    strategy_content_type = forms.ChoiceField(label="Rating Schema", choices=[])
    media_type_content_type = forms.ChoiceField(
        label="What would you like to Review?", choices=[]
    )
