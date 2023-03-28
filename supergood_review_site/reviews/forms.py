from enum import Enum
from typing import Any, List, Optional, Type, Union

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.fields import ChoiceField

from supergood_review_site.media_types.models import AbstractMediaType
from supergood_review_site.reviews.models import Review
from supergood_review_site.strategies.base.models import AbstractStrategy
from supergood_review_site.utils import Utils

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
    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "media_type_content_type",
            "media_type_object_id",
            "strategy_content_type",
        ]
        labels = {
            "text": "Review",
            "completed_at_year": "Year",
        }

    media_type_content_type = forms.ChoiceField(
        label="What do you want to review?", choices=[]
    )
    strategy_content_type = forms.ChoiceField(label="Rating Schema", choices=[])

    completed_at_day = forms.TypedChoiceField(
        label="Day",
        required=False,
        choices=[(None, ""), *((i, i) for i in range(1, 32))],
        coerce=int,
        empty_value=None,
    )
    completed_at_month = forms.TypedChoiceField(
        label="Month",
        required=False,
        choices=[
            (None, ""),
            *MONTH_CHOICES,
        ],
        coerce=int,
        empty_value=None,
    )

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

        self.add_models_to_choice_field("media_type_content_type", self.media_types)
        self.add_models_to_choice_field("strategy_content_type", self.strategies)

    def add_models_to_choice_field(
        self,
        choice_field_name: str,
        models: Union[List[Type[AbstractStrategy]], List[Type[AbstractMediaType]]],
    ) -> None:
        """Plug in models' content_type_ids into ChoiceField for a ContentType relation.

        The ChoiceField functions like a homegrown ModelChoiceField that is
        json serializable and can be injected into vue templates.

        Args:
          choice_field_name:
            Name of a ChoiceField with a ForeignKey to the ContentType table.
          models:
            List of models whose content_type_ids will be added as choices to "field".
        """
        field = self.fields[choice_field_name]
        assert isinstance(field, ChoiceField)

        field.choices = []
        for model in models:
            model_content_type_id = Utils.get_content_type_id(model)
            stringified_model_content_type_id = str(model_content_type_id)
            model_name = model._meta.verbose_name
            choice = (stringified_model_content_type_id, model_name)
            field.choices.append(choice)

    def clean_strategy_content_type(self) -> ContentType:
        """Convert content_type_id into actual ContentType model."""
        data = self.cleaned_data["strategy_content_type"]
        content_type_id = int(data)
        content_type_model = ContentType.objects.get_for_id(content_type_id)
        return content_type_model

    def clean_media_type_content_type(self) -> ContentType:
        """Convert content_type_id into actual ContentType model."""
        data = self.cleaned_data["media_type_content_type"]
        content_type_id = int(data)
        content_type_model = ContentType.objects.get_for_id(content_type_id)
        return content_type_model

    def clean(self) -> Any:
        cleaned_data = super().clean()
        return cleaned_data


class CreateNewMediaOption(Enum):
    SELECT_EXISTING = "SELECT_EXISTING"
    CREATE_NEW = "CREATE_NEW"


class ReviewMgmtForm(forms.Form):
    create_new_media_type_object = ChoiceField(
        label="Select existing or create new?",
        choices=[
            (CreateNewMediaOption.SELECT_EXISTING.value, "Select Existing"),
            (CreateNewMediaOption.CREATE_NEW.value, "Create New"),
        ],
        initial=CreateNewMediaOption.SELECT_EXISTING.value,
    )

    def clean_create_new_media_type_object(self) -> bool:
        data = self.cleaned_data["create_new_media_type_object"]
        should_create_new: bool = data == CreateNewMediaOption.CREATE_NEW.value
        return should_create_new
