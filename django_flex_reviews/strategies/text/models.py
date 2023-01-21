from django.db import models
from django.conf import settings
from strategies.base.models import BaseStategy


class TextStrategy(BaseStategy):
    """
    The Text Strategy only has a text field, but no quantitative ranking schema.
    """
    text = models.TextField(blank=True, null=True)
