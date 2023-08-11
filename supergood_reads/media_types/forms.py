from typing import TypeVar

from django import forms
from django.db.models.base import Model
from django.urls import reverse

from .models import Book, Film

_M = TypeVar("_M", bound=Model)


class MediaTypeAutocomplete(forms.ModelForm[_M]):
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


class BookAutocompleteForm(MediaTypeAutocomplete[Book]):
    autocomplete_url_name = "book_autocomplete"

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "year",
            "pages",
        ]


class FilmAutocompleteForm(MediaTypeAutocomplete[Film]):
    autocomplete_url_name = "film_autocomplete"

    class Meta:
        model = Film
        fields = [
            "title",
            "director",
            "year",
        ]


class MyMediaBookForm(forms.ModelForm[Book]):
    class Meta:
        model = Book
        fields = ["title", "author", "year"]


class MyMediaFilmForm(forms.ModelForm[Film]):
    class Meta:
        model = Film
        fields = ["title", "director", "year"]
