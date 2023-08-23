from django import forms

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
