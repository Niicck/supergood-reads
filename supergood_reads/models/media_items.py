import uuid
from typing import Any, Self, TypeVar, cast

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

from supergood_reads.models.review import Review

_T = TypeVar("_T", bound="BaseMediaItem")


class MediaItemQuerySet(models.QuerySet[_T]):
    def with_autocomplete_label(self) -> Self:
        return self.annotate(autocomplete_label=self.model.autocomplete_label())


class MediaItemManager(models.Manager[_T]):
    def get_queryset(self) -> MediaItemQuerySet[_T]:
        return MediaItemQuerySet[_T](self.model, using=self._db)


class BaseMediaItemQuerySet(models.QuerySet["BaseMediaItem"]):
    def with_select_related(self, *models: type["BaseMediaItem"]) -> Self:
        return self.select_related([m.__name__.lower() for m in models])


class BaseMediaItem(models.Model):
    """
    Base class common to all MediaItems.

    Subclasses can add any additional fields they'd like.
    But they must also define:
    - "creator" property
    - "icon" property
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, db_index=True
    )
    title = models.CharField(default="", max_length=256, db_index=True)
    year = models.IntegerField(
        blank=True, null=True, validators=[MaxValueValidator(9999)]
    )
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False, db_index=True)
    validated = models.BooleanField(default=False, db_index=True)

    reviews = GenericRelation(
        Review,
        object_id_field="media_item_object_id",
        content_type_field="media_item_content_type",
    )

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return self.title

    @property
    def media_item(self) -> str:
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
        A user can only update a MediaItem instance only if:
          - The user owns the Review
          - The user has global "change_[model]" permission
        """
        from supergood_reads.views.auth import has_owner_permission, has_perm_dynamic

        return has_owner_permission(user, self) or has_perm_dynamic(
            user, self, "change"
        )

    def can_user_delete(self, user: User | AnonymousUser) -> bool:
        """
        A user can only update a MediaItem instance only if:
          - The user owns the Review
          - The user has global "change_[model]" permission
        """
        from supergood_reads.views.auth import has_owner_permission, has_perm_dynamic

        return has_owner_permission(user, self) or has_perm_dynamic(
            user, self, "delete"
        )

    def get_child(self: _T) -> _T:
        from supergood_reads.utils.engine import supergood_reads_engine

        for model_class in supergood_reads_engine.media_item_model_classes:
            model_name = model_class.__name__.lower()
            if hasattr(self, model_name):
                return cast(_T, getattr(self, model_name))

        return self

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        now = timezone.now()
        if self._state.adding:
            self.created_at = now
        self.updated_at = now
        super().save(*args, **kwargs)


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self) -> str:
        return self.name


class GenreMixin(models.Model):
    genres = models.ManyToManyField(Genre)

    class Meta:
        abstract = True


class Book(BaseMediaItem, GenreMixin):
    """
    A handwritten or printed work of fiction or nonfiction, usually on sheets of paper
    fastened or bound together within covers.
    """

    author = models.CharField(default="", max_length=256)
    pages = models.IntegerField(blank=True, null=True)

    objects = MediaItemManager["Book"]()

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


class CountryMixin(models.Model):
    countries = models.ManyToManyField(Country)

    class Meta:
        abstract = True


class Film(BaseMediaItem, GenreMixin, CountryMixin):
    """
    A sequence of consecutive still images recorded in a series to be viewed on a screen
    in such rapid succession as to give the illusion of natural movement; motion
    picture.
    """

    director = models.CharField(default="", max_length=256)

    objects = MediaItemManager["Film"]()

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
