from enum import Enum
from typing import Any, List, Optional, Type

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.forms.fields import ChoiceField

from supergood_review_site.reviews.models import Review
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
    strategy_choices: Optional[List[Type[Model]]]
    media_type_choices: Optional[List[Type[Model]]]

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
        strategy_choices: List[Type[Model]],
        media_type_choices: List[Type[Model]],
        **kwargs: Any
    ) -> None:
        """
        Kwargs:
          strategy_choices:
            list of strategies to be used in strategy_content_type dropdown field
          media_type_choices:
            list of media_type models to be used in media_type_content_type dropdown field
        """
        super().__init__(*args, **kwargs)

        self.strategy_choices = strategy_choices
        self.media_type_choices = media_type_choices

        self.populate_generic_foreign_key_choice_field(
            "strategy_content_type", self.strategy_choices
        )
        self.populate_generic_foreign_key_choice_field(
            "media_type_content_type", self.media_type_choices
        )

    def populate_generic_foreign_key_choice_field(
        self,
        choice_field_name: str,
        models: List[Type[Model]],
    ) -> None:
        """Add models as choices to a ChoiceField for a GenericForeignKey.

        This allows users to select the ContentType model they want to use for a
        GenericForeignKey.

        This ChoiceField functions very similarly to a ModelChoiceField, except that it
        is json serializable and can easily be injected into vue templates.

        Example:
            self.add_models_to_choice_field(
                "strategy_content_type",
                [EbertStrategy, GoodreadsStrategy, MaximusStrategy]
            )

            Will add:
              ("7", "Ebert"),
              ("8", "Goodreads"),
              ("9", "Maximus")
            To:
              self.strategy_content_type ChoiceField

        Args:
          choice_field_name:
            Name of a ChoiceField for a ForeignKey to the ContentType table.
          models:
            List of models whose content_type_ids will be added as choices.
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


class UpdateMyReviewForm(forms.ModelForm[Review]):
    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            # TODO: strategy
            "text",
        ]
