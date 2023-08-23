from typing import Any

from django import forms
from django.forms.fields import ChoiceField

from supergood_reads.media_types.models import Book, Film


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
    media_type_content_type = forms.TypedChoiceField(
        label="Media Type", choices=[], required=True, coerce=int
    )

    def __init__(
        self,
        media_type_forms: list[forms.ModelForm[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        field = self.fields["media_type_content_type"]
        assert isinstance(field, ChoiceField)
        field.choices = media_type_forms.as_form_choices

    @property
    def selected_media_type_content_type_id(self) -> bool:
        return self.cleaned_data.get("media_type_content_type")
