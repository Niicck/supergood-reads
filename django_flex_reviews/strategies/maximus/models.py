from django.db import models
from strategies.base.models import AbstractStategyBase


class MaximusStrategy(AbstractStategyBase):
    """
    The Maximus Strategy is a simple yes/no boolean strategy.
    """

    text = models.TextField(blank=True, null=True)
    recommended = models.BooleanField(null=False)
