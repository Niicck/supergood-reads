from enum import Enum
from typing import Any, Optional, cast

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms import ModelForm
from django.forms.fields import ChoiceField

from supergood_reads.forms.base import ContentTypeChoiceField, GenericRelationFormGroup
from supergood_reads.models import AbstractReviewStrategy, BaseMediaItem, Review
from supergood_reads.utils.engine import supergood_reads_engine

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

        MediaItemModelClass = content_type.model_class()  # noqa: N806
        if not MediaItemModelClass:
            raise InvalidContentTypeError

        # Raises MediaItemModelClass.DoesNotExist if not foud
        content_type.get_object_for_this_type(id=object_id)
    except (ContentType.DoesNotExist, InvalidContentTypeError):
        form.add_error(
            content_type_field_name,
            "The selected content type does not exist.",
        )
        return False
    except (MediaItemModelClass.DoesNotExist, InvalidObjectIdError):
        form.add_error(object_id_field_name, "The selected object does not exist.")
        return False
    return True


class ReviewForm(forms.ModelForm[Review]):
    strategy_choices: list[type[AbstractReviewStrategy]]
    media_item_choices: list[type[BaseMediaItem]]

    class Meta:
        model = Review
        fields = [
            "completed_at_day",
            "completed_at_month",
            "completed_at_year",
            "text",
            "media_item_content_type",
            "media_item_object_id",
            "strategy_content_type",
        ]
        labels = {
            "text": "Review",
            "completed_at_year": "Year",
            "media_item_object_id": "Title",
        }

    media_item_content_type = ContentTypeChoiceField(
        label="Media Type",
        parent_model=BaseMediaItem,
        required=True,
        empty_label=None,
    )
    strategy_content_type = ContentTypeChoiceField(
        label="Rating Strategy",
        parent_model=AbstractReviewStrategy,
        required=True,
        empty_label=None,
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
        strategy_choices: Optional[list[type[AbstractReviewStrategy]]] = None,
        media_item_choices: Optional[list[type[BaseMediaItem]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Kwargs:
          strategy_choices:
            list of strategies to be used in strategy_content_type dropdown field
          media_item_choices:
            list of media_item models to be used in media_item_content_type dropdown field
        """
        super().__init__(*args, **kwargs)

        self.strategy_choices = strategy_choices or []
        self.media_item_choices = media_item_choices or []

        media_item_choice_field = cast(
            ContentTypeChoiceField, self.fields["media_item_content_type"]
        )
        media_item_choice_field.set_models(self.media_item_choices)

        strategy_choice_field = cast(
            ContentTypeChoiceField, self.fields["strategy_content_type"]
        )
        strategy_choice_field.set_models(self.strategy_choices)


class CreateNewMediaOption(Enum):
    SELECT_EXISTING = "SELECT_EXISTING"
    CREATE_NEW = "CREATE_NEW"


class ReviewMgmtForm(forms.Form):
    create_new_media_item_object = ChoiceField(
        label="Select existing or create new?",
        choices=[
            (CreateNewMediaOption.SELECT_EXISTING.value, "Select Existing"),
            (CreateNewMediaOption.CREATE_NEW.value, "Create New"),
        ],
        initial=CreateNewMediaOption.SELECT_EXISTING.value,
    )

    def clean_create_new_media_item_object(self) -> bool:
        data = self.cleaned_data["create_new_media_item_object"]
        should_create_new: bool = data == CreateNewMediaOption.CREATE_NEW.value
        return should_create_new

    @property
    def should_create_new_media_item_object(self) -> bool:
        return self.cleaned_data.get("create_new_media_item_object") or False


class ReviewFormGroup:
    review_form: ReviewForm
    review_mgmt_form: ReviewMgmtForm
    strategy_forms: GenericRelationFormGroup
    media_item_forms: GenericRelationFormGroup
    review: Review

    def __init__(
        self,
        data: Optional[Any] = None,
        instance: Optional[Review] = None,
        user: Optional[User] = None,
        initial: dict[str, Any] | None = None,
    ) -> None:
        self.data = data
        self.instance = instance
        self.user = user
        self.initial = initial or {}
        self.valid: Optional[bool] = None
        self.original_strategy = self._get_original_strategy()
        self.instantiate_forms()

    def _get_original_strategy(self) -> AbstractReviewStrategy | None:
        if self.instance and self.instance.strategy:
            return cast(AbstractReviewStrategy, self.instance.strategy)
        return None

    def instantiate_forms(self) -> None:
        self.review_form = ReviewForm(
            prefix="review",
            data=self.data,
            instance=self.instance,
            strategy_choices=supergood_reads_engine.strategy_model_classes,
            media_item_choices=supergood_reads_engine.media_item_model_classes,
            initial=self.initial.get("review_form"),
        )

        self.review_mgmt_form = ReviewMgmtForm(
            prefix="review_mgmt",
            data=self.data,
        )

        selected_strategy_id: Optional[int] = self._get_content_type_id(
            "strategy_content_type"
        )
        self.strategy_forms = GenericRelationFormGroup(
            supergood_reads_engine.strategy_form_classes,
            selected_form_id=selected_strategy_id,
            data=self.data,
            instance=self.original_strategy,
        )

        selected_media_item_id: Optional[int] = self._get_content_type_id(
            "media_item_content_type"
        )
        self.media_item_forms = GenericRelationFormGroup(
            supergood_reads_engine.media_item_form_classes,
            selected_form_id=selected_media_item_id,
            data=self.data,
        )

    def _get_content_type_id(self, field_name: str) -> int | None:
        """Get content_type_id value from ContentTypeChoiceField."""
        field = self.review_form[field_name]
        if not type(field.field) == ContentTypeChoiceField:
            return None
        content_type_id: str | int | None = field.value()
        if isinstance(content_type_id, str):
            try:
                content_type_id = int(content_type_id)
            except ValueError:
                content_type_id = None
        return content_type_id

    @transaction.atomic
    def is_valid(self) -> bool:
        self.valid = True

        if not self.review_form.is_valid():
            self.valid = False

        if not self.review_mgmt_form.is_valid():
            self.valid = False

        if self.review_mgmt_form.should_create_new_media_item_object:
            # Check that form for new MediaItem is valid
            selected_media_item_form = self.media_item_forms.selected_form
            if not selected_media_item_form or not selected_media_item_form.is_valid():
                self.valid = False
        else:
            # Check that selected existing MediaItem is valid
            media_item_object_id = self.review_form.cleaned_data.get(
                "media_item_object_id"
            )
            if not media_item_object_id:
                # If we aren't creating a new media_item object, then an existing
                # media_item object_id must be selected.
                self.review_form.add_error(
                    "media_item_object_id", "This field is required."
                )
                self.valid = False
            else:
                media_item_valid = validate_generic_foreign_key(
                    self.review_form, "media_item_object_id", "media_item_content_type"
                )
                if not media_item_valid:
                    self.valid = False

        selected_strategy_form = self.strategy_forms.selected_form
        if not selected_strategy_form or not selected_strategy_form.is_valid():
            self.valid = False

        return self.valid

    @transaction.atomic
    def save(self) -> Review:
        """Save the Review and any associated Foriegn Models"""
        if self.valid is None:
            self.is_valid()
        if not self.valid:
            raise ValueError("Failed to save Review. At least one form is invalid.")

        review = self.review_form.save(commit=False)

        if self.review_mgmt_form.should_create_new_media_item_object:
            selected_media_item_form = self.media_item_forms.selected_form
            assert selected_media_item_form
            media_item = selected_media_item_form.save(commit=False)
            media_item.owner = self.user
            media_item.save()
            review.media_item = media_item

        # If we've chosen a new strategy, delete the old strategy instance.
        if self.original_strategy and (
            "strategy_content_type" in self.review_form.changed_data
        ):
            self.original_strategy.delete()
        selected_strategy_form = self.strategy_forms.selected_form
        assert selected_strategy_form
        strategy = selected_strategy_form.save()
        review.strategy = strategy

        if self.review_form.instance._state.adding:
            review.owner = self.user

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
