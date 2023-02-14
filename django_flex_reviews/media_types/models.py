from django.db import models


class AbstractMedia(models.Model):
    """Abstract class common to all Media."""

    class Meta:
        abstract = True
