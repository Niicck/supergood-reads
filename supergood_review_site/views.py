import logging
from typing import Any, Dict, List, Optional, Type

from django import forms
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from supergood_review_site.media_types.forms import BookForm, FilmForm
from supergood_review_site.media_types.models import AbstractMediaType, Book, Film
from supergood_review_site.reviews.forms import ReviewForm, ReviewMgmtForm
from supergood_review_site.strategies.base.models import AbstractStrategy
from supergood_review_site.strategies.ebert.forms import EbertStrategyForm
from supergood_review_site.strategies.goodreads.forms import GoodreadsStrategyForm
from supergood_review_site.strategies.maximus.forms import MaximusStrategyForm
from supergood_review_site.utils import Utils
from supergood_review_site.utils.json import UUIDEncoder

logger = logging.getLogger(__name__)


class CreateReviewView(TemplateView):
    template_name = "supergood_review_site/create_review.html"
    strategy_forms: List[Type[forms.ModelForm[Any]]] = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_forms: List[Type[forms.ModelForm[Any]]] = [
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
        context["review_mgmt_form"] = ReviewMgmtForm(prefix="review_mgmt")
        context["strategy_forms"] = self.initialize_forms(self.strategy_forms)
        context["media_type_forms"] = self.initialize_forms(self.media_type_forms)

        return context

    def initialize_forms(
        self,
        forms: List[Type[forms.ModelForm[Any]]],
        post_data: Optional[Any] = None,
        selected_content_type_id: Optional[int] = None,
    ) -> Dict[str, forms.ModelForm[Any]]:
        """Add a list of forms to the context of the rendered template.

        Args:
            forms:
              list of forms to initialize
            post_data:
              optional request.POST data to handle form submissions.
            selected_content_type_id:
              The content_type_id for the model that was selected to be filled out by
              the client. The form associated with this model is the only form that will
              have post_data applied to it.

        The returned context object uses the content_type_id as the dictionary key.
        This is because the ReviewForm uses the model's content_type_id to select
        which model to use. The Review model relates to Strategy and MediaType via a
        GenericForeignKey, which makes it necessary to specify which model we are
        relating to.

        By identifying our ModelForms by their model's content_type_id, our template
        can select the correct ModelForm by the content_type selected in the ReviewForm.

        Example:
            self.initialize_forms(self.strategy_forms)

            Returns:
                {
                    "7": EbertStrategyForm(),
                    "8": GoodreadsStrategyForm(),
                    "9": MaximusStrategyForm(),
                }
        """
        initialized_forms = {}
        for form in forms:
            form_model = form()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = Utils.get_content_type_id(form_model)
            stringified_model_content_type_id = str(model_content_type_id)
            if post_data and model_content_type_id == selected_content_type_id:
                initialized_form = form(post_data, prefix=model_name)
            else:
                initialized_form = form(prefix=model_name)
            initialized_forms[stringified_model_content_type_id] = initialized_form
        return initialized_forms

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if settings.DEBUG:
            request_data = dict(request.POST.items())
            logger.info(request_data)

        any_invalid = False

        # Validate ReviewForm
        review_form = ReviewForm(
            request.POST,
            prefix="review",
            strategies=self.strategy_form_models,
            media_types=self.media_type_form_models,
        )
        if not review_form.is_valid():
            any_invalid = True

        # Validate ReviewMgmtForm
        review_mgmt_form = ReviewMgmtForm(request.POST, prefix="review_mgmt")
        if not review_mgmt_form.is_valid():
            any_invalid = True

        # Validate MediaType forms
        should_create_new_media_type_object = review_mgmt_form.cleaned_data.get(
            "create_new_media_type_object"
        )
        selected_media_type_content_type = review_form.cleaned_data.get(
            "media_type_content_type"
        )
        if should_create_new_media_type_object and selected_media_type_content_type:
            media_type_forms = self.initialize_forms(
                self.media_type_forms,
                post_data=request.POST,
                selected_content_type_id=selected_media_type_content_type.id,
            )
            selected_media_type_form = media_type_forms[
                str(selected_media_type_content_type.id)
            ]
            if not selected_media_type_form.is_valid():
                any_invalid = True
        else:
            media_type_forms = self.initialize_forms(
                self.media_type_forms, post_data=request.POST
            )
            selected_media_type_form = None

        if (
            not should_create_new_media_type_object
            and not review_form.cleaned_data.get("media_type_object_id")
        ):
            review_form.add_error("media_type_object_id", "This field is required.")
            any_invalid = True

        # Validate Strategy forms
        selected_strategy_content_type = review_form.cleaned_data.get(
            "strategy_content_type"
        )
        if selected_strategy_content_type:
            strategy_forms = self.initialize_forms(
                self.strategy_forms,
                post_data=request.POST,
                selected_content_type_id=selected_strategy_content_type.id,
            )
            selected_strategy_form = strategy_forms[
                str(selected_strategy_content_type.id)
            ]
            if not selected_strategy_form.is_valid():
                any_invalid = True
        else:
            strategy_forms = self.initialize_forms(
                self.strategy_forms, post_data=request.POST
            )
            selected_strategy_form = None
            any_invalid = True

        # If any forms are invalid, render the form again with error messages.
        if any_invalid:
            messages.error(request, "Please fix the errors below.")
            return render(
                request,
                self.template_name,
                {
                    "review_form": review_form,
                    "review_mgmt_form": review_mgmt_form,
                    "strategy_forms": strategy_forms,
                    "media_type_forms": media_type_forms,
                },
                status=400,
            )

        # Save to database
        try:
            with transaction.atomic():
                review = review_form.save(commit=False)
                if should_create_new_media_type_object:
                    assert selected_media_type_form
                    media_type = selected_media_type_form.save()
                    review.media_type_object_id = media_type.id
                assert selected_strategy_form
                strategy = selected_strategy_form.save()
                review.strategy_object_id = strategy.id
                review.save()
        except Exception:
            logger.exception("Failed to create Review")
            messages.error(request, "Server Error.")
            return render(
                request,
                self.template_name,
                {
                    "review_form": review_form,
                    "review_mgmt_form": review_mgmt_form,
                    "strategy_forms": strategy_forms,
                    "media_type_forms": media_type_forms,
                },
                status=500,
            )
        if review.media_type:
            messages.success(request, f"Added review for {review.media_type.title}.")
        return redirect("create_review")


class FilmAutocompleteView(View):
    limit = 20

    def get(self, request: HttpRequest) -> JsonResponse:
        query_dict = request.GET
        q = query_dict.get("q", "")
        films = Film.objects.filter(title__icontains=q).annotate(
            display_name=Concat(
                "title",
                Value(" ("),
                "release_year",
                Value(")"),
                output_field=CharField(),
            )
        )[: self.limit]
        film_values = films.values("id", "title", "display_name")

        return JsonResponse(
            {
                "results": list(film_values),
            },
            encoder=UUIDEncoder,
        )


class BookAutocompleteView(View):
    limit = 20

    def get(self, request: HttpRequest) -> JsonResponse:
        query_dict = request.GET
        q = query_dict.get("q", "")
        books = Book.objects.filter(title__icontains=q).annotate(
            display_name=Concat(
                "title",
                Value(" ("),
                "author",
                Value(", "),
                "publication_year",
                Value(")"),
                output_field=CharField(),
            )
        )[: self.limit]
        book_values = books.values("id", "title", "display_name")

        return JsonResponse(
            {
                "results": list(book_values),
            },
            encoder=UUIDEncoder,
        )
