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
    if review.media_type:
        assert isinstance(review.media_type, AbstractMediaType)
        initial_title = review.media_type.title
        initial_media_type = review.media_type.media_type
    else:
        initial_title = ""
        initial_media_type = ""
    json_script_id = f"{review.id}_json_script_id"

    return {
        "review": review,
        "json_script_id": json_script_id,
        "initial_data": {
            "initialTitle": initial_title,
            "initialMediaType": initial_media_type,
            "initialCompletedAt": review.completed_at,
            "initialRating": "★★★★★",  # TODO: make this work, raw html?
            "initialText": review.text,
        },
        "form": UpdateMyReviewForm(instance=review),
    }
