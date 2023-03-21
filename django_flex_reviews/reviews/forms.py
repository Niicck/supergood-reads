from typing import Any, List, Optional, Type, Union

from django import forms
from django.forms.fields import ChoiceField

from django_flex_reviews.media_types.models import AbstractMediaType
from django_flex_reviews.reviews.models import Review
from django_flex_reviews.strategies.base.models import AbstractStrategy
from django_flex_reviews.utils import Utils

MONTH_CHOICES = (
    (1, "Jan"),
    (2, "Feb"),
    (3, "Mar"),
    (4, "Apr"),
    (5, "May"),
    (6, "Jun"),
    (7, "Jul"),
    (8, "Aug"),
    (9, "Sep"),
    (10, "Oct"),
    (11, "Nov"),
    (12, "Dec"),
)


class ReviewForm(forms.ModelForm[Review]):
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
        self,
        content_type_field_name: str,
        models: Union[List[Type[AbstractStrategy]], List[Type[AbstractMediaType]]],
    ) -> None:
        """Plug in models' content_type_ids into ChoiceField for a ContentType relation.

        Args:
          content_type_field_name:
            Name of the ChoiceField to add choices to. This should be a ForeignKey to
            the ContentType table.
          models:
            List of models that can be selected from the content_type_field
        """
        content_type_field = self.fields[content_type_field_name]
        assert isinstance(content_type_field, ChoiceField)
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
            "media_type_object_id",
        ]
        labels = {
            "text": "Review",
            "completed_at_year": "Year",
        }

    strategy_content_type = forms.ChoiceField(label="Rating Schema", choices=[])
    media_type_content_type = forms.ChoiceField(
        label="What do you want to review?", choices=[]
    )
    completed_at_day = forms.ChoiceField(
        label="Day",
        required=False,
        choices=[(None, ""), *((i, i) for i in range(1, 32))],
    )
    completed_at_month = forms.ChoiceField(
        label="Month",
        required=False,
        choices=[
            (None, ""),
            *MONTH_CHOICES,
        ],
    )


class ReviewMgmtForm(forms.Form):
    """Adds helper fields that aren't explicitly part of Review Model."""

    create_new_media_type_object = forms.ChoiceField(
        label="Select existing or create new?",
        choices=[
            (False, "Select Existing"),
            (True, "Create New"),
        ],
    )
