from typing import Generic, TypeVar

from django import forms
from django.urls import reverse

from .models import Book, Film

MediaTypeT = TypeVar("MediaTypeT")


class MediaTypeAutocomplete(forms.ModelForm[Generic[MediaTypeT]]):
    """ModelForm that includes option to select an existing model via autocomplete.

    Properties:
      autocomplete_url:
        The url to the autocomplete view. Allows users to search for and select an
        existing model instance rather than create a new one.
    """

    autocomplete_url_name: str

    @property
    def autocomplete_url(self) -> str:
        return reverse(self.autocomplete_url_name)


class BookForm(MediaTypeAutocomplete[Book]):
    autocomplete_url_name = "book_autocomplete"

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "publication_year",
            "pages",
        ]


class FilmForm(MediaTypeAutocomplete[Film]):
    autocomplete_url_name = "film_autocomplete"

    class Meta:
        model = Film
        fields = [
            "title",
            "director",
            "release_year",
        ]
