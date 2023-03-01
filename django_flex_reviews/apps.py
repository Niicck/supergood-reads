from enum import Enum
from typing import Optional, Type

from django import forms
from django.apps import AppConfig
from django.conf import settings


def apply_default_settings() -> None:
    """Apply default setting values on app start up."""
    import django_flex_reviews.media_types.models as media_types
    import django_flex_reviews.strategies.models as strategies
    from django_flex_reviews.strategies.ebert.forms import EbertStrategyForm
    from django_flex_reviews.strategies.goodreads.forms import GoodreadsStrategyForm
    from django_flex_reviews.strategies.maximus.forms import MaximusStrategyForm

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
        DJANGO_FLEX_REVIEW_STRATEGY_FORMS: list[Type[forms.ModelForm]] = [
            EbertStrategyForm,
            GoodreadsStrategyForm,
            MaximusStrategyForm,
        ]

        """
        Eligible strategies to choose from when writing a review.
        If you create any custom media models, you will have to add them to this list.

        Example:
            DJANGO_FLEX_REVIEW_MEDIA_CHOICES = (
                django_flex_reviews.default_settings.DEFAULT_MEDIA_CHOICES +
                MyNewMediaType
            )
        """
        DJANGO_FLEX_REVIEW_MEDIA_CHOICES: list[Type[media_types.AbstractMediaType]] = [
            media_types.Film,
            media_types.Book,
        ]

        """
        This is the default strategy that will applied to a new Review.

        If you use UserStrategyDefaults, you can more finely tune the default strategies
        per user, per media type.
        """
        DJANGO_FLEX_REVIEW_DEFAULT_STRATEGY: Optional[
            Type[strategies.AbstractStrategy]
        ] = None

    for setting in DefaultSettings:
        if not hasattr(settings, setting.name):
            setattr(settings, setting.name, setting.value)


class DjangoFlexReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_flex_reviews"

    def ready(self) -> None:
        apply_default_settings()
