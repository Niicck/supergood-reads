from typing import Any, Dict

from django import template
from django.utils.safestring import SafeText

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
        if year is None:
            year_str = "unknown"
        else:
            year_str = str(year)
        icon = review.media_type.icon()
        title = title + f" ({year_str})"
    else:
        icon = SafeText("")
        title = ""
    if isinstance(review.strategy, AbstractStrategy):
        rating_html = review.strategy.rating_html
    else:
        rating_html = SafeText("")

    return {
        "review": review,
        "title": title,
        "icon": icon,
        "rating_html": rating_html,
    }
