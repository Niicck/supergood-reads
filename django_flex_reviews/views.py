from typing import Any, Dict, List, Type

from django import forms
from django.views.generic import TemplateView

from django_flex_reviews.media_types.forms import BookForm, FilmForm
from django_flex_reviews.media_types.models import AbstractMediaType
from django_flex_reviews.reviews.forms import ReviewForm
from django_flex_reviews.strategies.base.models import AbstractStrategy
from django_flex_reviews.strategies.ebert.forms import EbertStrategyForm
from django_flex_reviews.strategies.goodreads.forms import GoodreadsStrategyForm
from django_flex_reviews.strategies.maximus.forms import MaximusStrategyForm
from django_flex_reviews.utils import Utils


class CreateReviewView(TemplateView):
    template_name = "create_review.html"
    strategy_forms = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_forms = [
        BookForm,
        FilmForm,
    ]

    @property
    def strategy_form_models(self) -> List[Type[AbstractStrategy]]:
        return [form()._meta.model for form in self.strategy_forms]

    @property
    def media_type_form_models(self) -> List[Type[AbstractMediaType]]:
        return [form()._meta.model for form in self.media_type_forms]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["review_form"] = ReviewForm(
            prefix="review",
            strategies=self.strategy_form_models,
            media_types=self.media_type_form_models,
        )

        context = self.add_forms_to_context(
            context, "strategy_forms", self.strategy_forms
        )
        context = self.add_forms_to_context(
            context, "media_type_forms", self.media_type_forms
        )

        return context

    def add_forms_to_context(
        self,
        context: Dict[str, Any],
        form_group_name: str,
        forms: List[Type[forms.ModelForm]],
    ) -> Dict[str, Any]:
        """Add a list of forms to the context of the rendered template.

        Args:
            context:
                the existing context_data object.
            form_group_name:
                the key used to access the forms on the context object
            forms:
                list of forms to add under the form_group_name in the context

        The returned context object uses the content_type_id as the dictionary key.
        This is because the ReviewForm uses the model's content_type_id to select
        which model to use. The ReviewForm connects to strategy and media_type via a
        GenericForeignKey, which makes it necessary to specify which model we are
        relating to.

        By identifying our ModelForms by their model's content_type_id, our template
        can select the correct ModelForm by the content_type selected in the ReviewForm.

        Example:
            self.add_forms_to_context(context, "strategy_forms", self.strategy_forms)

            Returns:

                {
                    "strategy_forms": {
                        7: EbertStrategyForm(),
                        8: GoodreadsStrategyForm(),
                        9: MaximusStrategyForm(),
                    }
                }
        """
        context[form_group_name] = {}
        for form in forms:
            form_model = form()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = Utils.get_content_type_id(form_model)
            context[form_group_name][model_content_type_id] = form(prefix=model_name)
        return context
