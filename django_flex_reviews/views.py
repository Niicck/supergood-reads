from typing import Any, Dict

from django.views.generic import TemplateView

from django_flex_reviews.reviews.forms import ReviewForm
from django_flex_reviews.strategies.ebert.forms import EbertStrategyForm
from django_flex_reviews.strategies.goodreads.forms import GoodreadsStrategyForm
from django_flex_reviews.strategies.maximus.forms import MaximusStrategyForm

strategy_model_forms = [
    EbertStrategyForm,
    GoodreadsStrategyForm,
    MaximusStrategyForm,
]


class CreateReviewView(TemplateView):
    template_name = "create_review.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["review_form"] = ReviewForm(prefix="review")
        context["strategy_forms"] = {}

        for strategy_model_form in strategy_model_forms:
            model_name = strategy_model_form._meta.model._meta.model_name  # type: ignore[attr-defined]
            context["strategy_forms"][f"{model_name}_form"] = strategy_model_form(
                prefix=model_name
            )

        return context
