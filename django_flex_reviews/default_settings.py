from enum import Enum
from typing import Optional, Type

from django.conf import settings


def apply_default_settings() -> None:
    """Apply default setting values on app start up."""
    from django_flex_reviews.media_types.models import AbstractMediaType
    from django_flex_reviews.strategies.base.models import AbstractStrategy

    class DefaultSettings(Enum):
        """Default values for django.conf.settings introduced by django_flex_reviews."""

        """
        Eligible strategies to choose from when writing a review.
        If you create any custom strategy models, you will have to add them to this list.

        Example:
            DJANGO_FLEX_REVIEW_STRATEGY_CHOICES = (
                django_flex_reviews.default_settings.DEFAULT_STRATEGY_CHOICES +
                MyNewStrategy
            )
        """
        DJANGO_FLEX_REVIEW_STRATEGY_CHOICES: list[Type[AbstractStrategy]] = []

        """
        Eligible strategies to choose from when writing a review.
        If you create any custom media models, you will have to add them to this list.

        Example:
            DJANGO_FLEX_REVIEW_MEDIA_CHOICES = (
                django_flex_reviews.default_settings.DEFAULT_MEDIA_CHOICES +
                MyNewMediaType
            )
        """
        DJANGO_FLEX_REVIEW_MEDIA_CHOICES: list[Type[AbstractMediaType]] = []

        """
        This is the default strategy that will applied to a new Review.

        If you use UserStrategyDefaults, you can more finely tune the default strategies
        per user, per media type.
        """
        DJANGO_FLEX_REVIEW_DEFAULT_STRATEGY: Optional[Type[AbstractStrategy]] = None

    for setting in DefaultSettings:
        if not hasattr(settings, setting.name):
            setattr(settings, setting.name, setting.value)
