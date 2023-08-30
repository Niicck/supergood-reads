from typing import Any, Optional, cast

from django import forms
from django.contrib.auth.models import User
from django.db import transaction

from supergood_reads.common.forms import (
    ContentTypeChoiceField,
    GenericRelationFormGroup,
)
from supergood_reads.media_types.models import AbstractMediaType, Book, Film
from supergood_reads.utils import ContentTypeUtils


class BookForm(forms.ModelForm[Book]):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "year",
            "pages",
        ]


class FilmForm(forms.ModelForm[Film]):
    class Meta:
        model = Film
        fields = [
            "title",
            "director",
            "year",
        ]


class LibraryBookForm(BookForm):
    class Meta:
        model = Book
        fields = ["title", "author", "year"]


class LibraryFilmForm(FilmForm):
    pass


class MediaMgmtForm(forms.Form):
    """Select which MediaType you want to create."""

    media_type_content_type = ContentTypeChoiceField(
        label="Media Type",
        parent_model=AbstractMediaType,
        required=True,
        empty_label=None,
    )

    def __init__(
        self,
        *args: Any,
        instance: AbstractMediaType | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        media_type_field = cast(
            ContentTypeChoiceField, self.fields["media_type_content_type"]
        )

        from supergood_reads.utils.engine import supergood_reads_engine

        media_type_field.set_models(supergood_reads_engine.media_type_model_classes)

        if instance:
            media_type_field.disabled = True
            media_type_field.initial = ContentTypeUtils.get_content_type_id(instance)


class MediaTypeFormGroup:
    media_type_forms: GenericRelationFormGroup
    media_mgmt_form: MediaMgmtForm
    media_item: AbstractMediaType

    def __init__(
        self,
        data: Optional[Any] = None,
        instance: Optional[AbstractMediaType] = None,
        user: Optional[User] = None,
    ) -> None:
        self.data = data
        self.instance = instance
        self.user = user
        self.valid: Optional[bool] = None
        self.instantiate_forms()

    def instantiate_forms(self) -> None:
        from supergood_reads.utils.engine import supergood_reads_engine

        self.media_mgmt_form = MediaMgmtForm(
            data=self.data, instance=self.instance, prefix="media_type_mgmt"
        )

        selected_media_type_id: int | None = None
        if self.media_mgmt_form.is_valid():
            media_type_content_type = self.media_mgmt_form.cleaned_data.get(
                "media_type_content_type"
            )
            if media_type_content_type:
                selected_media_type_id = media_type_content_type.id
        else:
            selected_media_type_id = self.media_mgmt_form[
                "media_type_content_type"
            ].value()

        self.media_type_forms = GenericRelationFormGroup(
            supergood_reads_engine.media_type_form_classes,
            selected_form_id=selected_media_type_id,
            data=self.data,
            instance=self.instance,
        )

    @transaction.atomic
    def is_valid(self) -> bool:
        self.valid = True

        if not self.media_mgmt_form.is_valid():
            self.valid = False

        selected_media_type_form = self.media_type_forms.selected_form
        if not selected_media_type_form or not selected_media_type_form.is_valid():
            self.valid = False

        return self.valid

    @transaction.atomic
    def save(self) -> AbstractMediaType:
        """Save the Review and any associated Foriegn Models"""
        if self.valid is None:
            self.is_valid()
        if not self.valid:
            raise ValueError(
                "Media Form could not be saved because the data didn't validate."
            )

        selected_media_type_form = self.media_type_forms.selected_form
        assert selected_media_type_form

        media_item: AbstractMediaType = selected_media_type_form.save(commit=False)

        if not media_item.owner:
            media_item.owner = self.user

        media_item.save()
        self.media_item = media_item
        return media_item
