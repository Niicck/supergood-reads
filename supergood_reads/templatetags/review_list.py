from typing import Any, Dict

from django import template
from django.utils.safestring import SafeText

from supergood_reads.models import AbstractReviewStrategy, BaseMediaItem, Review

register = template.Library()


@register.inclusion_tag("supergood_reads/views/review_list/_review_list_row.html")
def review_list_row(
    review: Review,
) -> Dict[str, Any]:
    if isinstance(review.media_item, BaseMediaItem):
        title = review.media_item.title
        year = review.media_item.year
        if year is None:
            year_str = "(unknown)"
        else:
            year_str = f"({str(year)})"
        icon = review.media_item.icon()
    else:
        icon = SafeText("")
        title = ""
        year_str = ""
    if isinstance(review.strategy, AbstractReviewStrategy):
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
