from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from supergood_review_site.strategies.base.models import AbstractStrategy


class ImdbStrategy(AbstractStrategy):
    """Replicate IMDB scoring strategy.

    Score from 1 to 10.
    Null values are not allowed.
    """

    score = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
