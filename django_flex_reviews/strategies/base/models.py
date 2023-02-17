import uuid

from django.db import models


class AbstractStrategy(models.Model):
    """Abstract class common to all Strategies."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    @property
    def display_rating(self) -> str:
        return ""
