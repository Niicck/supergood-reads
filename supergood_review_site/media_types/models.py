import uuid
from typing import Any

from django.db import models
from django.utils import timezone


class AbstractMediaType(models.Model):
    """Abstract class common to all MediaTypes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(default="", max_length=256)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        now = timezone.now()
        if self._state.adding:
            self.created_at = now
        self.updated_at = now
        super().save(*args, **kwargs)


class Genre(models.Model):
    genre = models.CharField(max_length=256, unique=True)

    def __str__(self) -> str:
        return self.genre


class Book(AbstractMediaType):
    """
    A handwritten or printed work of fiction or nonfiction, usually on sheets of paper
    fastened or bound together within covers.
    """

    author = models.CharField(default="", max_length=256)
    pages = models.IntegerField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True, max_length=4)
    genres = models.ManyToManyField(Genre)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Book"


class Country(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self) -> str:
        return self.name


class Film(AbstractMediaType):
    """
    A sequence of consecutive still images recorded in a series to be viewed on a screen
    in such rapid succession as to give the illusion of natural movement; motion
    picture.
    """

    director = models.CharField(default="", max_length=256)
    release_year = models.IntegerField(blank=True, null=True, max_length=4)
    genres = models.ManyToManyField(Genre)
    countries = models.ManyToManyField(Country)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Film"
