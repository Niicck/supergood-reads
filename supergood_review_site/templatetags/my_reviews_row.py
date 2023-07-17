from typing import Any, Dict

from django import template

from supergood_review_site.media_types.models import AbstractMediaType
from supergood_review_site.reviews.forms import UpdateMyReviewForm
from supergood_review_site.reviews.models import Review

register = template.Library()


@register.inclusion_tag("supergood_review_site/_my_reviews_row.html")
def my_reviews_row(
    review: Review,
) -> Dict[str, Any]:
    assert isinstance(review.media_type, AbstractMediaType)
    json_script_id = f"{review.id}_json_script_id"

    return {
        "review": review,
        "json_script_id": json_script_id,
        "initial_data": {
            "initialTitle": review.media_type.title,
            "initialMediaType": review.media_type.media_type,
            "initialCompletedAt": review.completed_at,
            "initialRating": "★★★★★",  # TODO: make this work, raw html?
            "initialText": review.text,
        },
        "form": UpdateMyReviewForm(instance=review),
    }
