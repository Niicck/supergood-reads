from typing import Any, Dict, List, Type

from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView

from django_flex_reviews.reviews.forms import ReviewForm
from django_flex_reviews.strategies.base.models import AbstractStrategy
from django_flex_reviews.strategies.ebert.forms import EbertStrategyForm
from django_flex_reviews.strategies.goodreads.forms import GoodreadsStrategyForm
from django_flex_reviews.strategies.maximus.forms import MaximusStrategyForm


class CreateReviewView(TemplateView):
    template_name = "create_review.html"
    strategy_forms = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]

    @property
    def strategy_form_models(self) -> List[Type[AbstractStrategy]]:
        return [strategy_form()._meta.model for strategy_form in self.strategy_forms]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["review_form"] = ReviewForm(
            prefix="review", strategies=self.strategy_form_models
        )

        context["strategy_forms"] = {}
        for strategy_model_form in self.strategy_forms:
            strategy_model = strategy_model_form()._meta.model
            model_name = strategy_model._meta.model_name
            model_content_type_id = ContentType.objects.get_for_model(strategy_model).id
            context["strategy_forms"][model_content_type_id] = strategy_model_form(
                prefix=model_name
            )

        return context
