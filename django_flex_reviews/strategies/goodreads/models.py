from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_flex_reviews.strategies.base.models import AbstractStrategy


class GoodreadsStrategy(AbstractStrategy):
    """Replicate Goodreads scoring strategy.

    The Goodreads Strategy is a star rating from 1 to 5.
    Null values are not allowed.
    """

    stars = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = "Goodreads"
