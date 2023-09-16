import math
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import SafeText


class AbstractReviewStrategy(models.Model):
    """
    Abstract class common to all Strategies.

    Subclasses can add any fields they want.
    But they must implement:
    - "rating_html" property for rendering with "reviews" table
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    @property
    def rating_html(self) -> SafeText:
        return format_html("")


def ebert_star_validator(value: Decimal) -> None:
    """Ensure that star rating is valid."""
    if not value:
        return
    elif value < 0:
        raise ValidationError("Star rating can't be less than zero")
    elif value > 4:
        raise ValidationError("Star rating can't be greater than 4")
    elif value % Decimal("0.5") != 0:
        raise ValidationError("Star rating must be a multiple of 0.5")


class EbertStrategy(AbstractReviewStrategy):
    """Replicate Roger Ebert's film scoring strategy.

    Star rating from 0 to 4.
    Null values are allowed.
    There is also a "GOAT" boolean value to indicate 4-star MediaItems that are among
    the "Greatest of all Time."
    """

    stars = models.DecimalField(
        decimal_places=1,
        max_digits=2,
        null=True,
        validators=[ebert_star_validator],
    )
    goat = models.BooleanField(default=False, null=False)

    class Meta:
        verbose_name = "Ebert"

    @property
    def rating_html(self) -> SafeText:
        if self.goat:
            value = "GOAT"
            return format_html("<span class='goat-font text-gray-900'>{}</span>", value)
        elif self.stars is None:
            value = "No Star Rating"
        elif self.stars == Decimal("0.0"):
            value = "Zero Stars"
        else:
            star_count = math.floor(self.stars)
            remainder = self.stars % 1
            value = "★" * star_count
            if remainder:
                value += "½"
        return format_html("<span class='text-gray-900'>{}</span>", value)


class GoodreadsStrategy(AbstractReviewStrategy):
    """Replicate Goodreads scoring strategy.

    The Goodreads Strategy is a star rating from 1 to 5.
    Null values are not allowed.
    """

    stars = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = "Goodreads"

    @property
    def rating_html(self) -> SafeText:
        stars = "★" * self.stars
        remainder = 5 - self.stars
        empty_stars = "★" * remainder
        return format_html(
            "<span class='text-orange-500'>{}</span><span class='text-slate-200'>{}</span>",
            stars,
            empty_stars,
        )


class ImdbStrategy(AbstractReviewStrategy):
    """Replicate IMDB scoring strategy.

    Score from 1 to 10.
    Null values are not allowed.
    """

    score = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        verbose_name = "IMDB"

    @property
    def rating_html(self) -> SafeText:
        return format_html(
            "<span class='text-amber-400'>★</span><span class='text-gray-900'> {} / 10</span>",
            self.score,
        )


def letterboxd_star_validator(value: Decimal) -> None:
    """Ensure that star rating is valid."""
    if value < Decimal("0.5"):
        raise ValidationError("Star rating can't be less than .5")
    elif value > 5:
        raise ValidationError("Star rating can't be greater than 5")
    elif value % Decimal("0.5") != 0:
        raise ValidationError("Star rating must be a multiple of 0.5")


class LetterboxdStrategy(AbstractReviewStrategy):
    """Replicate Letterboxd scoring strategy.

    Star rating from 0.5 to 5.0.
    Null values are not allowed.
    """

    stars = models.DecimalField(
        decimal_places=1,
        max_digits=2,
        null=False,
        validators=[letterboxd_star_validator],
    )

    class Meta:
        verbose_name = "Letterboxd"

    @property
    def rating_html(self) -> SafeText:
        star_count = math.floor(self.stars)
        remainder = self.stars % 1
        value = "★" * star_count
        if remainder:
            value += "½"
        return format_html("<span class='text-green-400'>{}</span>", value)


class ThumbsStrategy(AbstractReviewStrategy):
    """Replicate Joaquin Phoenix's scoring strategy from Gladiator (2000).

    Simple yes/no boolean strategy.
    """

    recommended = models.BooleanField(null=False)

    class Meta:
        verbose_name = "Thumbs"

    @property
    def rating_html(self) -> SafeText:
        if self.recommended:
            template_name = "supergood_reads/components/svg/thumbs_up.html"
        else:
            template_name = "supergood_reads/components/svg/thumbs_down.html"
        value = render_to_string(template_name)
        return format_html("<span class='text-emerald-600'>{}</span>", value)


class TomatoStrategy(AbstractReviewStrategy):
    """Simple yes/no boolean strategy."""

    fresh = models.BooleanField(null=False)

    class Meta:
        verbose_name = "Tomatoes"

    @property
    def rating_html(self) -> SafeText:
        if self.fresh:
            return format_html("<span>🍅</span>")
        else:
            template_name = "supergood_reads/components/svg/rotten.html"
            value = render_to_string(template_name)
            return format_html("<span class='text-lime-700'>{}</span>", value)
