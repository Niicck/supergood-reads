from enum import Enum
from typing import Any, Dict, List, Optional, Type, cast

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm
from django.forms.fields import ChoiceField

from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.reviews.models import Review
from supergood_reads.strategies.models import AbstractStrategy
from supergood_reads.utils import ContentTypeUtils
from supergood_reads.utils.engine import supergood_reads_engine
from supergood_reads.utils.forms import get_initial_field_value

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


class InvalidObjectIdError(Exception):
    pass


def validate_generic_foreign_key(
    form: ModelForm[Any], object_id_field_name: str, content_type_field_name: str
) -> bool:
    """
    Make sure that the form's "content_type" value is a valid ContentType.
    And make sure that the associated "object_id" is a valid id for the ContentType's Model.
    """
    try:
        object_id = form.cleaned_data.get(object_id_field_name)
        if not object_id:
            raise InvalidObjectIdError

        content_type = form.cleaned_data.get(content_type_field_name)
        if not content_type:
            raise InvalidContentTypeError

        MediaTypeModelClass = content_type.model_class()  # noqa: N806
        if not MediaTypeModelClass:
            raise InvalidContentTypeError

        # Raises MediaTypeModelClass.DoesNotExist if not foud
        content_type.get_object_for_this_type(id=object_id)
    except (ContentType.DoesNotExist, InvalidContentTypeError):
        form.add_error(
            content_type_field_name,
            "The selected content type does not exist.",
        )
        return False
    except (MediaTypeModelClass.DoesNotExist, InvalidObjectIdError):
        form.add_error(object_id_field_name, "The selected object does not exist.")
        return False
    return True


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

    media_type_content_type = forms.TypedChoiceField(
        label="What do you want to review?", choices=[], required=True, coerce=int
    )
    strategy_content_type = forms.TypedChoiceField(
        label="Rating Schema", choices=[], required=True, coerce=int
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
        strategy_choices: Optional[List[Type[Model]]] = None,
        media_type_choices: Optional[List[Type[Model]]] = None,
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
        selected_form_id: The content_type_id for the model whose form was selected to
          be filled out by the client.
        data: optional request.POST data to handle form submissions.
        instance: pre-existing instance that is being updated.

    """

    def __init__(
        self,
        form_classes: List[Type[ModelForm[Any]]],
        selected_form_id: Optional[int] = None,
        data: Optional[Any] = None,
        instance: Optional[Model] = None,
    ) -> None:
        self.form_classes = form_classes
        self.selected_form_id = selected_form_id
        self.data = data
        self.instance = instance
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

        if self.instance:
            instance_content_type_id = ContentTypeUtils.get_content_type_id(
                self.instance
            )
        else:
            instance_content_type_id = None

        for form_class in self.form_classes:
            form_model = form_class()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = ContentTypeUtils.get_content_type_id(form_model)

            # Plug in instance or data into selected_form
            if (
                self.instance or self.data
            ) and model_content_type_id == self.selected_form_id:
                if instance_content_type_id and (
                    instance_content_type_id == self.selected_form_id
                ):
                    instance = self.instance
                else:
                    instance = None
                instantiated_form = form_class(
                    self.data, instance=instance, prefix=model_name
                )
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
        self.original_strategy = self._get_original_strategy()
        self.instantiate_forms()

    def _get_original_strategy(self) -> AbstractStrategy | None:
        if self.instance and self.instance.strategy:
            return cast(AbstractStrategy, self.instance.strategy)
        return None

    def instantiate_forms(self) -> None:
        self.review_form = ReviewForm(
            prefix="review",
            data=self.data,
            instance=self.instance,
            strategy_choices=supergood_reads_engine.config.strategy_model_classes,
            media_type_choices=supergood_reads_engine.config.media_type_model_classes,
        )

        selected_strategy_id = self._get_content_type_id("strategy_content_type")
        selected_media_type_id = self._get_content_type_id("media_type_content_type")

        self.review_mgmt_form = ReviewMgmtForm(
            prefix="review_mgmt",
            data=self.data,
        )

        strategy_instance = self.instance and self.instance.strategy
        self.strategy_forms = GenericRelationFormGroup(
            supergood_reads_engine.config.strategy_form_classes,
            selected_form_id=selected_strategy_id,
            data=self.data,
            instance=strategy_instance,
        )

        self.media_type_forms = GenericRelationFormGroup(
            supergood_reads_engine.config.media_type_form_classes,
            selected_form_id=selected_media_type_id,
            data=self.data,
        )

    def _get_content_type_id(self, field_name: str) -> int | None:
        """
        Retrieve the content type ID associated with the specified form field.
        """
        selected_content_type_id: str | int | None = get_initial_field_value(
            self.review_form, field_name
        )
        if isinstance(selected_content_type_id, str):
            try:
                selected_content_type_id = int(selected_content_type_id)
            except ValueError:
                selected_content_type_id = None
        return selected_content_type_id

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
        else:
            media_type_object_id = self.review_form.cleaned_data.get(
                "media_type_object_id"
            )
            if not media_type_object_id:
                # If we aren't creating a new media_type object, then an existing
                # media_type object_id must be selected.
                self.review_form.add_error(
                    "media_type_object_id", "This field is required."
                )
                self.valid = False
            else:
                media_type_valid = validate_generic_foreign_key(
                    self.review_form, "media_type_object_id", "media_type_content_type"
                )
                if not media_type_valid:
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

        # If we've chosen a new strategy, delete the old strategy instance.
        if self.original_strategy and (
            "strategy_content_type" in self.review_form.changed_data
        ):
            self.original_strategy.delete()
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
