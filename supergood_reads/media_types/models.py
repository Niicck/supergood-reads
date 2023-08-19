import uuid
from typing import Any, Self, TypeVar

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import SafeText

from supergood_reads.reviews.models import Review

_T = TypeVar("_T", bound="AbstractMediaType")


class MediaTypeQuerySet(models.QuerySet[_T]):
    def with_autocomplete_label(self) -> Self:
        return self.annotate(autocomplete_label=self.model.autocomplete_label())


class MediaTypeManager(models.Manager[_T]):
    def get_queryset(self) -> MediaTypeQuerySet[_T]:
        return MediaTypeQuerySet[_T](self.model, using=self._db)


class AbstractMediaType(models.Model):
    """
    Abstract class common to all MediaTypes.

    Subclasses can add any additional fields they'd like.
    But they must also define:
    - "creator" property
    - "icon" property
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    title = models.CharField(default="", max_length=256)
    year = models.IntegerField(
        blank=True, null=True, validators=[MaxValueValidator(9999)]
    )
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)
    validated = models.BooleanField(default=False)

    reviews = GenericRelation(
        Review,
        object_id_field="media_type_object_id",
        content_type_field="media_type_content_type",
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title

    @property
    def media_type(self) -> str:
        return str(self._meta.verbose_name)

    @property
    def creator(self) -> str:
        raise NotImplementedError

    @classmethod
    def icon(cls) -> SafeText:
        raise NotImplementedError

    @classmethod
    def autocomplete_label(cls) -> Any:
        return F("title")

    def can_user_change(self, user: User | AnonymousUser) -> bool:
        """
        A user can only update a MediaType instance only if:
          - The user owns the Review
          - The user has global "change_[model]" permission
        """
        from supergood_reads.auth import has_owner_permission, has_perm_dynamic

        return has_owner_permission(user, self) or has_perm_dynamic(
            user, self, "change"
        )

    def can_user_delete(self, user: User | AnonymousUser) -> bool:
        """
        A user can only update a MediaType instance only if:
          - The user owns the Review
          - The user has global "change_[model]" permission
        """
        from supergood_reads.auth import has_owner_permission, has_perm_dynamic

        return has_owner_permission(user, self) or has_perm_dynamic(
            user, self, "delete"
        )

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
    genres = models.ManyToManyField(Genre)

    objects = MediaTypeManager["Book"]()

    class Meta:
        verbose_name = "Book"

    def __str__(self) -> str:
        return self.title

    @property
    def creator(self) -> str:
        return self.author

    @classmethod
    def icon(cls) -> SafeText:
        value = render_to_string("supergood_reads/components/svg/book.html")
        return format_html("<span class='text-xs text-cyan-500'>{}</span>", value)

    @classmethod
    def autocomplete_label(cls) -> Any:
        return Concat(
            "title",
            Value(" ("),
            "author",
            Value(", "),
            "year",
            Value(")"),
            output_field=CharField(),
        )


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
    genres = models.ManyToManyField(Genre)
    countries = models.ManyToManyField(Country)

    objects = MediaTypeManager["Film"]()

    class Meta:
        verbose_name = "Film"

    def __str__(self) -> str:
        return self.title

    @property
    def creator(self) -> str:
        return self.director

    @classmethod
    def icon(cls) -> SafeText:
        value = render_to_string("supergood_reads/components/svg/film.html")
        return format_html("<span class='text-xs text-cyan-500'>{}</span>", value)

    @classmethod
    def autocomplete_label(cls) -> Any:
        return Concat(
            "title",
            Value(" ("),
            "year",
            Value(")"),
            output_field=CharField(),
        )
