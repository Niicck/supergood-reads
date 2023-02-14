"""Replicate Joaquin Phoenix's scoring strategy from Gladiator (2000)."""
from django.db import models

from django_flex_reviews.strategies.base.models import AbstractStrategy


class MaximusStrategy(AbstractStrategy):
    """The Maximus Strategy is a simple yes/no boolean strategy."""

    recommended = models.BooleanField(null=False)
