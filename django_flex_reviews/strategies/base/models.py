from django.db import models


class AbstractStrategy(models.Model):
    """Abstract class common to all Strategies."""

    class Meta:
        abstract = True

    @property
    def display_rating(self) -> str:
        return ""
