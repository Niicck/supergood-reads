from typing import Any, Dict

from django import template
from django.utils.safestring import SafeText

from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.reviews.models import Review
from supergood_reads.strategies.models import AbstractStrategy

register = template.Library()


@register.inclusion_tag("supergood_reads/_review_row.html")
def review_row(
    review: Review,
) -> Dict[str, Any]:
    if isinstance(review.media_type, AbstractMediaType):
        title = review.media_type.title
        year = review.media_type.year
        if year is None:
            year_str = "(unknown)"
        else:
            year_str = f"({str(year)})"
        icon = review.media_type.icon()
    else:
        icon = SafeText("")
        title = ""
        year_str = ""
    if isinstance(review.strategy, AbstractStrategy):
        rating_html = review.strategy.rating_html
    else:
        rating_html = SafeText("")

    return {
        "review": review,
        "title": title,
        "year": year_str,
        "icon": icon,
        "rating_html": rating_html,
    }
