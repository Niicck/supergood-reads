from django.db import models


class AbstractMediaType(models.Model):
    """Abstract class common to all MediaTypes."""

    title = models.CharField(default="", max_length=256)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


class Genre(models.Model):
    genre = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.genre


class Book(AbstractMediaType):
    """
    A handwritten or printed work of fiction or nonfiction, usually on sheets of paper
    fastened or bound together within covers.
    """

    author = models.CharField(default="", max_length=256)
    pages = models.IntegerField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)

    def __str__(self) -> str:
        return self.title


class Country(models.Model):
    country = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.country


class Film(AbstractMediaType):
    """
    A handwritten or printed work of fiction or nonfiction, usually on sheets of paper
    fastened or bound together within covers.
    """

    director = models.CharField(default="", max_length=256)
    release_year = models.IntegerField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    countries = models.ManyToManyField(Country)

    def __str__(self) -> str:
        return self.title
