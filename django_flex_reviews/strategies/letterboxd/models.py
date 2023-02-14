from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from django_flex_reviews.strategies.base.models import AbstractStrategy


def letterboxd_star_validator(value: Decimal) -> None:
    """Ensure that star rating is valid."""
    if value < Decimal("0.5"):
        raise ValidationError("Star rating can't be less than .5")
    elif value > 5:
        raise ValidationError("Star rating can't be greater than 5")
    elif value % Decimal("0.5") != 0:
        raise ValidationError("Star rating must be a multiple of 0.5")


class LetterboxdStrategy(AbstractStrategy):
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
