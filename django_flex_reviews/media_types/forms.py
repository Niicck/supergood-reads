from django import forms

from .models import Book, Film


class BookForm(forms.ModelForm[Book]):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "pages",
            "publication_year",
        ]


class FilmForm(forms.ModelForm[Film]):
    class Meta:
        model = Film
        fields = [
            "title",
            "director",
            "release_year",
        ]
