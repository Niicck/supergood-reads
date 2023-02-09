from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from strategies.base.models import AbstractStategyBase


def letterboxd_star_validator(value):
    if value < Decimal("0.5"):
        raise ValidationError("Star rating can't be less than .5")
    elif value > 5:
        raise ValidationError("Star rating can't be greater than 5")
    elif value % Decimal("0.5") != 0:
        raise ValidationError("Star rating must be a multiple of 0.5")


class LetterboxdStrategy(AbstractStategyBase):
    """
    The Letterboxd Strategy is a star ratings from 0.5 to 5.
    Null values are not allowed.
    """

    text = models.TextField(blank=True, null=True)
    stars = models.DecimalField(
        decimal_places=1,
        null=False,
        validators=[letterboxd_star_validator],
    )
