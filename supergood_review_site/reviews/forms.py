from enum import Enum
from typing import Any, Dict, List, Optional, Type

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm
from django.forms.fields import ChoiceField

from supergood_review_site.media_types.forms import (
    BookAutocompleteForm,
    FilmAutocompleteForm,
)
from supergood_review_site.media_types.models import AbstractMediaType
from supergood_review_site.reviews.models import Review
from supergood_review_site.strategies.base.models import AbstractStrategy
from supergood_review_site.strategies.ebert.forms import EbertStrategyForm
from supergood_review_site.strategies.goodreads.forms import GoodreadsStrategyForm
from supergood_review_site.strategies.maximus.forms import MaximusStrategyForm
from supergood_review_site.utils import ContentTypeUtils

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


class InvalidContentTypeError(Exception):
    pass


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
        label="What do you want to review?", choices=[], required=True
    )
    strategy_content_type = forms.ChoiceField(
        label="Rating Schema", choices=[], required=True
    )

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
        strategy_choices: List[Type[Model]] = None,
        media_type_choices: List[Type[Model]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Kwargs:
          strategy_choices:
            list of strategies to be used in strategy_content_type dropdown field
          media_type_choices:
            list of media_type models to be used in media_type_content_type dropdown field
        """
        super().__init__(*args, **kwargs)

        self.strategy_choices = strategy_choices or []
        self.media_type_choices = media_type_choices or []

        self.populate_generic_foreign_key_choice_field(
            "strategy_content_type", self.strategy_choices
        )
        self.populate_generic_foreign_key_choice_field(
            "media_type_content_type", self.media_type_choices
        )

    @property
    def strategy_content_type_id(self) -> Optional[int]:
        if hasattr(self, "cleaned_data"):
            selected_strategy_content_type = self.cleaned_data.get(
                "strategy_content_type"
            )
            if selected_strategy_content_type:
                assert isinstance(selected_strategy_content_type, ContentType)
                return selected_strategy_content_type.id
        return None

    @property
    def media_type_content_type_id(self) -> Optional[int]:
        if hasattr(self, "cleaned_data"):
            selected_media_type_content_type = self.cleaned_data.get(
                "media_type_content_type"
            )
            if selected_media_type_content_type:
                assert isinstance(selected_media_type_content_type, ContentType)
                return selected_media_type_content_type.id
        return None

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
            model_content_type_id = ContentTypeUtils.get_content_type_id(model)
            stringified_model_content_type_id = str(model_content_type_id)
            model_name = model._meta.verbose_name
            choice = (stringified_model_content_type_id, model_name)
            field.choices.append(choice)

    def clean_strategy_content_type(self) -> ContentType:
        """Convert content_type_id into actual ContentType model."""
        data = self.cleaned_data["strategy_content_type"]
        return self._clean_content_type(data, parent=AbstractStrategy)

    def clean_media_type_content_type(self) -> ContentType:
        """Convert content_type_id into actual ContentType model."""
        data = self.cleaned_data["media_type_content_type"]
        return self._clean_content_type(data, parent=AbstractMediaType)

    def _clean_content_type(self, data: Any, parent: Type[Model]) -> ContentType:
        """
        If form data was submitted with just the id of a ContentType, then convert it to
        a proper ContentType instance. Validate that ContentType model is a valid
        subclass of given parent."""
        parent_name = parent.__name__
        try:
            if isinstance(data, ContentType):
                content_type = data
                content_type_id = content_type.id
            else:
                content_type_id = int(data)
                content_type = ContentType.objects.get_for_id(content_type_id)
            model_class = content_type.model_class()
            if not (model_class and issubclass(model_class, parent)):
                raise InvalidContentTypeError()
        except (ContentType.DoesNotExist, InvalidContentTypeError):
            raise ValidationError(f"{content_type_id} is not a valid {parent_name}.")
        return content_type

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

    @property
    def should_create_new_media_type_object(self) -> bool:
        return self.cleaned_data.get("create_new_media_type_object") or False


class GenericRelationFormGroup:
    """Instantiate ModelForms for generic relations and associate them with their content_type_id.

    Args:
        form_classes: list of form classes to instantiate.
        data: optional request.POST data to handle form submissions.
        review_instance: pre-existing Review instance that is being updated.
        selected_form_id: The content_type_id for the model whose form was selected to
          be filled out by the client.
    """

    def __init__(
        self,
        form_classes: List[Type[ModelForm[Any]]],
        selected_form_id: Optional[int] = None,
        data: Optional[Any] = None,
        review_instance: Optional[Review] = None,
    ) -> None:
        self.form_classes = form_classes
        self.selected_form_id = selected_form_id
        self.data = data
        self.review_instance = review_instance
        self.by_content_type_id = self.instantiate_forms_by_content_type_id()
        self.selected_form = self.get_selected_form()

    def instantiate_forms_by_content_type_id(self) -> Dict[str, ModelForm[Any]]:
        """ "Organize forms by their content_type_id.

        This is useful in template rendering. A field can select a Model's
        content_type_id (like "7") and it can be connected to the desired ModelForm
        ("EbertStrategyForm").

        Example:
            self.forms = [EbertStrategyForm, GoodreadsStrategyForm, MaximusStrategyForm]
            self.forms_by_content_type_id -> {
                "7": EbertStrategyForm(),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
        """
        forms_by_content_type_id = {}
        for form_class in self.form_classes:
            form_model = form_class()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = ContentTypeUtils.get_content_type_id(form_model)

            # Initialize with data if current form was selected
            if self.data and model_content_type_id == self.selected_form_id:
                # TODO: handle existence of review_instance
                instantiated_form = form_class(self.data, prefix=model_name)
            else:
                instantiated_form = form_class(prefix=model_name)
            forms_by_content_type_id[str(model_content_type_id)] = instantiated_form
        return forms_by_content_type_id

    def get_selected_form(self) -> Optional[ModelForm[Any]]:
        """Returns selected Form.

        Example:
            self.selected_form_id = 7
            self.forms_by_content_type_id = {
                "7": EbertStrategyForm(),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
            self.selected_form -> EbertStrategyForm()
        """
        if self.selected_form_id:
            return self.by_content_type_id[str(self.selected_form_id)]
        return None


class ReviewFormGroup:
    strategy_form_classes: List[Type[ModelForm[Any]]] = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_form_classes: List[Type[ModelForm[Any]]] = [
        BookAutocompleteForm,
        FilmAutocompleteForm,
    ]
    review_form: ReviewForm
    review_mgmt_form: ReviewMgmtForm
    strategy_forms: GenericRelationFormGroup
    media_type_forms: GenericRelationFormGroup
    review: Review

    def __init__(
        self, data: Optional[Any] = None, instance: Optional[Review] = None
    ) -> None:
        self.data = data
        self.instance = instance
        self.valid: Optional[bool] = None
        self.validate_strategy_form_classes()
        self.validate_media_type_form_classes()
        self.instantiate_forms()

    @property
    def strategy_model_classes(self) -> List[Type[Model]]:
        return [form._meta.model for form in self.strategy_form_classes]

    @property
    def media_type_model_classes(self) -> List[Type[Model]]:
        return [form._meta.model for form in self.media_type_form_classes]

    def validate_strategy_form_classes(self) -> None:
        """Validate that all strategy_form_classes are Strategies."""
        for form_class in self.strategy_form_classes:
            if not issubclass(form_class._meta.model, AbstractStrategy):
                raise ValueError(
                    f"{form_class.__name__} is not a valid Strategy form class."
                )

    def validate_media_type_form_classes(self) -> None:
        """Validate that media_type_form_classes are MediaTypes."""
        for form_class in self.media_type_form_classes:
            if not issubclass(form_class._meta.model, AbstractMediaType):
                raise ValueError(
                    f"{form_class.__name__} is not a valid MediaType form class."
                )

    def instantiate_forms(self) -> None:
        self.review_form = ReviewForm(
            prefix="review",
            data=self.data,
            instance=self.instance,
            strategy_choices=self.strategy_model_classes,
            media_type_choices=self.media_type_model_classes,
        )
        # Set review_form's cleaned_data so GenericRelationFormGroups can get
        # selected content_type_ids.
        self.review_form.is_valid()

        self.review_mgmt_form = ReviewMgmtForm(
            prefix="review_mgmt",
            data=self.data,
        )

        self.strategy_forms = GenericRelationFormGroup(
            self.strategy_form_classes,
            selected_form_id=self.review_form.strategy_content_type_id,
            data=self.data,
        )

        self.media_type_forms = GenericRelationFormGroup(
            self.media_type_form_classes,
            selected_form_id=self.review_form.media_type_content_type_id,
            data=self.data,
        )

    def is_valid(self) -> bool:
        self.valid = True

        if not self.review_form.is_valid():
            self.valid = False

        if not self.review_mgmt_form.is_valid():
            self.valid = False

        if self.review_mgmt_form.should_create_new_media_type_object:
            selected_media_type_form = self.media_type_forms.selected_form
            if not selected_media_type_form or not selected_media_type_form.is_valid():
                self.valid = False
        elif not self.review_form.cleaned_data.get("media_type_object_id"):
            # If we aren't creating a new media_type object, then an existing
            # media_type object_id must be selected.
            self.review_form.add_error(
                "media_type_object_id", "This field is required."
            )
            self.valid = False

        selected_strategy_form = self.strategy_forms.selected_form
        if not selected_strategy_form or not selected_strategy_form.is_valid():
            self.valid = False

        return self.valid

    @transaction.atomic()
    def save(self) -> Review:
        """Save the Review and any associated Foriegn Models"""
        if self.valid is None:
            self.is_valid()
        if not self.valid:
            raise Exception("Failed to save Review. At least one form is invalid.")

        review = self.review_form.save(commit=False)

        if self.review_mgmt_form.should_create_new_media_type_object:
            selected_media_type_form = self.media_type_forms.selected_form
            assert selected_media_type_form
            media_type = selected_media_type_form.save()
            review.media_type = media_type

        selected_strategy_form = self.strategy_forms.selected_form
        assert selected_strategy_form
        strategy = selected_strategy_form.save()
        review.strategy = strategy

        review.save()
        self.review = review
        return review


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
