from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from django_flex_reviews.strategies.base.models import BaseStategy


def ebert_star_validator(value):
    if not value:
        return
    elif value < 0:
        raise ValidationError("Star rating can't be less than zero")
    elif value > 4:
        raise ValidationError("Star rating can't be greater than 4")
    elif value % Decimal("0.5") != 0:
        raise ValidationError("Star rating must be a multiple of 0.5")


class EbertStrategy(BaseStategy):
    """
    The Ebert Strategy is a star rating from 0 to 4.
    Null values are allowed.
    There is also a "Great Film" boolean value that supercedes the star rating.
    """

    text = models.TextField(blank=True, null=True)
    stars = models.DecimalField(
        decimal_places=1,
        null=True,
        validators=[ebert_star_validator],
    )
    great_film = models.BooleanField(default=False, null=False)
