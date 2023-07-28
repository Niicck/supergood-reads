from typing import Any, Dict

from django import template

from supergood_review_site.media_types.models import AbstractMediaType
from supergood_review_site.reviews.models import Review
from supergood_review_site.strategies.models import AbstractStrategy

register = template.Library()


@register.inclusion_tag("supergood_review_site/_reviews_row.html")
def reviews_row(
    review: Review,
) -> Dict[str, Any]:
    if isinstance(review.media_type, AbstractMediaType):
        title = review.media_type.title
        year = review.media_type.year
        icon = review.media_type.icon
        if year is None:
            year = "unknown"
        title = title + f" ({year})"
    else:
        icon = ""
        title = ""
    if isinstance(review.strategy, AbstractStrategy):
        rating_html = review.strategy.rating_html
    else:
        rating_html = ""

    return {
        "review": review,
        "title": title,
        "icon": icon,
        "rating_html": rating_html,
    }
