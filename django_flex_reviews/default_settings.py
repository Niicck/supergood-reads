from django.conf import settings

"""
Eligible strategies to choose from when writing a review.
If you create any custom strategy models, you will have to add them to this list.

Example:
    DJANGO_FLEX_REVIEW_STRATEGY_CHOICES = (
        django_flex_reviews.default_settings.DEFAULT_STRATEGY_CHOICES +
        MyNewStrategy
    )
"""
DEFAULT_STRATEGY_CHOICES = []


"""
Eligible strategies to choose from when writing a review.
If you create any custom media models, you will have to add them to this list.

Example:
    DJANGO_FLEX_REVIEW_MEDIA_CHOICES = (
        django_flex_reviews.default_settings.DEFAULT_MEDIA_CHOICES +
        MyNewMediaType
    )
"""
DEFAULT_MEDIA_CHOICES = []


"""
This is the default strategy that will applied to a new Review.

If you use UserStrategyDefaults, you can more finely tune the default strategies
per user, per media type.
"""
DEFAULT_DEFAULT_STRATEGY = None


DEFAULT_SETTINGS = {
    "DJANGO_FLEX_REVIEW_STRATEGY_CHOICES": DEFAULT_STRATEGY_CHOICES,
    "DJANGO_FLEX_REVIEW_MEDIA_CHOICES": DEFAULT_MEDIA_CHOICES,
    "DJANGO_FLEX_REVIEW_DEFAULT_STRATEGY": DEFAULT_DEFAULT_STRATEGY,
}


def apply_default_settings():
    for name, value in DEFAULT_SETTINGS.items():
        if not hasattr(settings, name):
            setattr(settings, name, value)
