"""
Eligible strategies to choose from when writing a review.
If you create any custom strategy models, you will have to add them to this list.

Example:
    DJANGO_FLEX_REVIEW_STRATEGY_CHOICES = (
        DJANGO_FLEX_REVIEW_STRATEGY_CHOICES + MyNewStrategy
    )
"""
DJANGO_FLEX_REVIEW_STRATEGY_CHOICES = []

"""
Eligible strategies to choose from when writing a review.
If you create any custom media models, you will have to add them to this list.

Example:
    DJANGO_FLEX_REVIEW_MEDIA_CHOICES = (
        DJANGO_FLEX_REVIEW_MEDIA_CHOICES + MyNewStrategy
    )
"""
DJANGO_FLEX_REVIEW_MEDIA_CHOICES = []

"""
This is the default strategy that will applied to a new Review.

You can more finely tune the default strategy you want to use by creating
UserStrategyDefaults per user per media type.
"""
DJANGO_FLEX_REVIEW_DEFAULT_STRATEGY = None
