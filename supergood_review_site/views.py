import logging
from typing import Any, Dict, List, Optional, Protocol, Type, cast

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import CharField, Model, QuerySet, Value
from django.db.models.functions import Concat
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from queryset_sequence import QuerySetSequence

from supergood_review_site.media_types.forms import (
    BookAutocompleteForm,
    FilmAutocompleteForm,
    MyMediaBookForm,
    MyMediaFilmForm,
)
from supergood_review_site.media_types.models import AbstractMediaType, Book, Film
from supergood_review_site.reviews.forms import ReviewForm, ReviewMgmtForm
from supergood_review_site.reviews.models import Review
from supergood_review_site.strategies.base.models import AbstractStrategy
from supergood_review_site.strategies.ebert.forms import EbertStrategyForm
from supergood_review_site.strategies.goodreads.forms import GoodreadsStrategyForm
from supergood_review_site.strategies.maximus.forms import MaximusStrategyForm
from supergood_review_site.utils import Utils
from supergood_review_site.utils.json import UUIDEncoder

logger = logging.getLogger(__name__)


class CreateReviewView(TemplateView):
    template_name = "supergood_review_site/create_review.html"
    strategy_form_classes: List[Type[ModelForm[Any]]] = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_form_classes: List[Type[ModelForm[Any]]] = [
        BookAutocompleteForm,
        FilmAutocompleteForm,
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Validate that strategy_form_classes are Strategies
        for form_class in self.strategy_form_classes:
            if not issubclass(form_class._meta.model, AbstractStrategy):
                raise ValueError(
                    f"{form_class.__name__} is not a valid Strategy form class."
                )

        # Validate that strategy_form_classes are Strategies
        for form_class in self.media_type_form_classes:
            if not issubclass(form_class._meta.model, AbstractMediaType):
                raise ValueError(
                    f"{form_class.__name__} is not a valid MediaType form class."
                )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        strategy_choices = FormModelExtractor(self.strategy_form_classes).run()
        media_type_choices = FormModelExtractor(self.media_type_form_classes).run()

        context["review_form"] = ReviewForm(
            prefix="review",
            strategy_choices=strategy_choices,
            media_type_choices=media_type_choices,
        )
        context["review_mgmt_form"] = ReviewMgmtForm(prefix="review_mgmt")
        context["strategy_forms"] = InstantiateGenericModelFormsHandler(
            self.strategy_form_classes
        ).run()
        context["media_type_forms"] = InstantiateGenericModelFormsHandler(
            self.media_type_form_classes
        ).run()

        return context

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if settings.DEBUG:
            request_data = dict(request.POST.items())
            logger.info(request_data)

        handler = ProcessReviewHandler(
            request, self.strategy_form_classes, self.media_type_form_classes
        )
        handler.run()

        # If any forms are invalid, render the form again with error messages.
        if handler.any_invalid:
            messages.error(request, "Please fix the errors below.")
            return render(
                request,
                self.template_name,
                {
                    "review_form": handler.review_form,
                    "review_mgmt_form": handler.review_mgmt_form,
                    "strategy_forms": handler.strategy_forms,
                    "media_type_forms": handler.media_type_forms,
                },
                status=400,
            )

        # If no forms are invalid, save Review to database
        try:
            handler.commit()
        except Exception:
            # If review fails to save, render the form again with error messages
            logger.exception("Failed to create Review")
            messages.error(request, "Server Error.")
            return render(
                request,
                self.template_name,
                {
                    "review_form": handler.review_form,
                    "review_mgmt_form": handler.review_mgmt_form,
                    "strategy_forms": handler.strategy_forms,
                    "media_type_forms": handler.media_type_forms,
                },
                status=500,
            )

        # Return successful response
        if handler.review.media_type:
            messages.success(
                request, f"Added review for {handler.review.media_type.title}."
            )
        return redirect("my_reviews")


class FormModelExtractor:
    """Extract the Models from a list of ModelForms.

    Example:
        FormModelExtractor([BookAutocompleteForm, FilmAutocompleteForm]).run()

        Returns:
            [Book, Film]
    """

    def __init__(self, forms: List[Type[ModelForm[Any]]]) -> None:
        self.forms = forms

    def run(self) -> List[Type[Model]]:
        self.extract_models_from_forms()
        return self.form_models

    def extract_models_from_forms(self) -> None:
        self.form_models = [self._extract_model(form) for form in self.forms]

    def _extract_model(self, form: Type[ModelForm[Any]]) -> Type[Model]:
        model = form._meta.model
        cast(Type[Model], model)
        return model


FormsByContentType = Dict[str, ModelForm[Any]]


class InstantiateGenericModelFormsHandler:
    """Instantiate ModelForms for generic relations and associate them with their content_type_id.

    Args:
        forms:
            list of forms to instantiate.
        post_data:
            optional request.POST data to handle form submissions.
        review_instance:
            pre-existing Review instance that is being updated.
        selected_content_type_id:
            The content_type_id for the model that was selected to be filled out by
            the client. The form associated with this model is the only form that will
            have post_data applied to it.

    Example 1:
        InstantiateGenericModelFormsHandler(strategy_forms).run()

        Returns:
            {
                "7": EbertStrategyForm(),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
    Example 2:
        InstantiateGenericModelFormsHandler(
            strategy_forms,
            post_data,
            selected_content_type_id="7"
        ).run()

        Returns:
            {
                "7": EbertStrategyForm(post_data),
                "8": GoodreadsStrategyForm(),
                "9": MaximusStrategyForm(),
            }
    """

    forms_by_content_type: FormsByContentType

    def __init__(
        self,
        forms: List[Type[ModelForm[Any]]],
        post_data: Optional[Any] = None,
        review_instance: Optional[Review] = None,
        selected_content_type_id: Optional[int] = None,
    ) -> None:
        self.forms = forms
        self.post_data = post_data
        self.review_instance = review_instance
        self.selected_content_type_id = selected_content_type_id

    def run(self) -> FormsByContentType:
        self.instantiate_forms_by_content_type()
        return self.forms_by_content_type

    def instantiate_forms_by_content_type(self) -> None:
        self.forms_by_content_type = {}
        for form in self.forms:
            form_model = form()._meta.model
            model_name = form_model._meta.model_name
            model_content_type_id = Utils.get_content_type_id(form_model)
            stringified_model_content_type_id = str(model_content_type_id)

            # Initialize with post_data if current form was selected
            if (
                self.post_data
                and model_content_type_id == self.selected_content_type_id
            ):
                # TODO: handle existence of review_instance
                instantiated_form = form(self.post_data, prefix=model_name)
            else:
                instantiated_form = form(prefix=model_name)
            self.forms_by_content_type[
                stringified_model_content_type_id
            ] = instantiated_form


class ProcessReviewHandler:
    """Process a POST request to create a new Review and any necessary foreign Models.

    Example:
        handler = ProcessReviewHandler(
            post_request,
            [EbertStrategy, GoodreadsStrategy, MaximusStrategy],
            [BookAutocompleteForm, FilmAutocompleteForm],
        )
        handler.run()
        if not handler.any_invalid:
            handler.commit()

    If all is successful, then no Exceptions will be raised and `handler.review` will
    contain the newly saved Review object.

    If any Exceptions occur, then the handler's forms can be re-rendered in the
    Template View and any mistakes can be corrected by the User:
        render(
            request,
            template_name,
            {
                "review_form": handler.review_form,
                "review_mgmt_form": handler.review_mgmt_form,
                "strategy_forms": handler.strategy_forms,
                "media_type_forms": handler.media_type_forms,
            },
        )

    Attributes:
        request: POST request data for creating a new Review.
        strategy_form_classes: eligible Strategy Form Classes for the Review.
        media_type_form_classes: eligible MediaType Form Classes for the Review.
        any_invalid: True if any required Form is not valid.
        review_form: instantiated ReviewForm bound with POST request data.
        review_mgmt_form: instantiated ReviewMgmtForm bound with POST request data.
        create_new_media_type_object: indicates whether the User chose to create a new
          media_type object (rather than selecting an existing one).
        media_type_forms: instantiated MediaType Forms bound with POST request data.
        selected_media_type_form: Form for the MediaType instance to be created for this Review.
        strategy_forms: instantiated Strategy Forms bound with POST request data.
        selected_strategy_form: Form for the Strategy instance to be created for this Review.
        review: the Review object that was created
    """

    review_form: ReviewForm
    review_mgmt_form: ReviewMgmtForm
    create_new_media_type_object: bool
    media_type_forms: FormsByContentType
    selected_media_type_form: Optional[ModelForm[Any]]
    strategy_forms: FormsByContentType
    selected_strategy_form: Optional[ModelForm[Any]]
    review: Review

    def __init__(
        self,
        request: HttpRequest,
        strategy_form_classes: List[Type[ModelForm[Any]]],
        media_type_form_classes: List[Type[ModelForm[Any]]],
    ) -> None:
        self.request = request
        self.strategy_form_classes = strategy_form_classes
        self.media_type_form_classes = media_type_form_classes
        self.any_invalid = False

    def run(self) -> None:
        self.validate_review_form()
        self.validate_review_mgmt_form()
        self.validate_media_type_form()
        self.validate_strategy_form()

    @transaction.atomic()
    def commit(self) -> None:
        self.save_review()

    def validate_review_form(self) -> None:
        """
        Validate that base ReviewForm is valid, without worrying about Strategies or
        MediaTypes yet.

        Assigns:
            review_form
        """
        strategy_choices = FormModelExtractor(self.strategy_form_classes).run()
        media_type_choices = FormModelExtractor(self.media_type_form_classes).run()
        self.review_form = ReviewForm(
            self.request.POST,
            prefix="review",
            strategy_choices=strategy_choices,
            media_type_choices=media_type_choices,
        )
        if not self.review_form.is_valid():
            self.any_invalid = True

    def validate_review_mgmt_form(self) -> None:
        """
        Validate ReviewMgmtForm, which contains metadata to help process the
        relationship between Review and its Generic Foreign Models.

        Assigns:
            review_mgmt_form
        """
        self.review_mgmt_form = ReviewMgmtForm(self.request.POST, prefix="review_mgmt")
        if not self.review_mgmt_form.is_valid():
            self.any_invalid = True

    def validate_media_type_form(self) -> None:
        """
        If User decided to create a new media_type object, then we need to validate the
        Form associated with that MediaType.

        Assigns:
            create_new_media_type_object
            media_type_forms
            selected_media_type_form
        """
        selected_media_type_content_type = self.review_form.cleaned_data.get(
            "media_type_content_type"
        )

        self.create_new_media_type_object: bool = (
            self.review_mgmt_form.cleaned_data.get("create_new_media_type_object")
            or False
        )

        media_form_to_bind: Optional[int] = None
        self.selected_media_type_form: Optional[ModelForm[AbstractMediaType]] = None

        # If User decided to create a new MediaType object, then we must bind
        # that ModelForm with request.POST data.
        if self.create_new_media_type_object and selected_media_type_content_type:
            cast(ContentType, selected_media_type_content_type)
            media_form_to_bind = selected_media_type_content_type.id

        # Instantiate all media_type_forms.
        # Even if we are not creating a new MediaType object, we still want to
        # instantiate these Forms anyway, in case we run into an error and need to
        # re-render our template and forms.
        self.media_type_forms = InstantiateGenericModelFormsHandler(
            self.media_type_form_classes,
            post_data=self.request.POST,
            selected_content_type_id=media_form_to_bind,
        ).run()

        # If User chose to create a new MediaType object (rather than selecting an
        # existing one) then validate that selected MediaType Form.
        if self.create_new_media_type_object and media_form_to_bind:
            self.selected_media_type_form = self.media_type_forms[
                str(media_form_to_bind)
            ]
            assert self.selected_media_type_form
            if not self.selected_media_type_form.is_valid():
                self.any_invalid = True

        # If User instead chose to select an existing MediaType object (rather than
        # creating a new one) then it should exist on the ReviewForm's
        # media_type_object_id field.
        if (
            not self.create_new_media_type_object
            and not self.review_form.cleaned_data.get("media_type_object_id")
        ):
            self.review_form.add_error(
                "media_type_object_id", "This field is required."
            )
            self.any_invalid = True
            return

    def validate_strategy_form(self) -> None:
        """
        Validate the Strategy Form used to score the Review.

        Assigns:
            strategy_forms
            selected_strategy_form
        """
        selected_strategy_content_type = self.review_form.cleaned_data.get(
            "strategy_content_type"
        )

        strategy_form_to_bind: Optional[int] = None
        self.selected_strategy_form: Optional[ModelForm[AbstractStrategy]] = None

        if selected_strategy_content_type:
            cast(ContentType, selected_strategy_content_type)
            strategy_form_to_bind = selected_strategy_content_type.id

        # Instantiate all strategy_forms.
        self.strategy_forms = InstantiateGenericModelFormsHandler(
            self.strategy_form_classes,
            post_data=self.request.POST,
            selected_content_type_id=strategy_form_to_bind,
        ).run()

        # If User did not select a Strategy, then the request is invalid.
        if not strategy_form_to_bind:
            self.any_invalid = True
            return

        # Validate selected_strategy_form
        self.selected_strategy_form = self.strategy_forms[str(strategy_form_to_bind)]
        assert self.selected_strategy_form
        if not self.selected_strategy_form.is_valid():
            self.any_invalid = True

    def save_review(self) -> None:
        """Save the Review and any associated Foriegn Models"""
        if self.any_invalid:
            raise Exception("Failed to save Review. At least one form is invalid.")

        self.review = self.review_form.save(commit=False)

        # Save MediaType
        if self.create_new_media_type_object:
            assert self.selected_media_type_form
            media_type = self.selected_media_type_form.save()
            self.review.media_type_object_id = media_type.id

        # Save Strategy
        assert self.selected_strategy_form
        strategy = self.selected_strategy_form.save()
        self.review.strategy_object_id = strategy.id

        # Save Review
        self.review.save()


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


class MyMediaView(ListView[AbstractMediaType]):
    model = AbstractMediaType
    paginate_by = 20
    context_object_name = "media_list"
    template_name = "supergood_review_site/my_media.html"

    def get_queryset(self) -> QuerySetSequence:
        """
        Return queryset combining all child content_types of AbstractMediaType.
        Ex: by default, this will return both Books and Films, ordered by "updated_at"
        in descending order.
        """
        media_types = AbstractMediaType.__subclasses__()
        combined_qs = QuerySetSequence(
            *[media_type.objects.all() for media_type in media_types],
            model=AbstractMediaType,
        )
        return combined_qs.order_by("-updated_at")


class MyReviewsView(ListView[Review]):
    model = Review
    paginate_by = 20
    context_object_name = "review_list"
    template_name = "supergood_review_site/my_reviews.html"

    def get_queryset(self) -> QuerySet[Review]:
        review_qs = (
            Review.objects.with_generic_relations()
            .all()
            .order_by("-completed_at_year", "-completed_at_month", "-completed_at_day")
        )
        return review_qs


class FormViewMixinProtocol(Protocol):
    @property
    def object(self) -> Any:
        ...

    @property
    def request(self) -> Any:
        ...

    def form_invalid(self, form: ModelForm[Any]) -> HttpResponseRedirect:
        ...

    def form_valid(self, form: ModelForm[Any]) -> HttpResponseRedirect:
        ...


class JsonableResponseMixin:
    """
    Mixin to add JSON response support to a form.
    Must be used with an object-based FormView (e.g. CreateView, UpdateView)
    """

    def form_invalid(self, form: ModelForm[Any]) -> JsonResponse:
        return JsonResponse({"errors": form.errors}, status=400)

    def form_valid(self, form: ModelForm[Any]) -> JsonResponse:
        self.object = form.save()
        data = {
            "id": self.object.pk,
            **{field: getattr(self.object, field) for field in form.fields},
        }
        return JsonResponse({"data": data})


class DeleteMyMediaMixin:
    def get_success_url(self: FormViewMixinProtocol) -> str:
        return reverse("my_media")

    def form_invalid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        messages.error(self.request, "Please fix the errors below.")
        return super().form_invalid(form)  # type: ignore[safe-super]

    def form_valid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        """
        Calls the delete() method on the fetched object and then
        returns pk.
        """
        title = self.object.title
        messages.success(self.request, f"Succesfully deleted {title}.")
        return super().form_valid(form)  # type: ignore[safe-super]


class UpdateMyMediaBookView(JsonableResponseMixin, UpdateView[Book, MyMediaBookForm]):
    """Update Book via ajax request."""

    object: Book
    model = Book
    form_class = MyMediaBookForm


class UpdateMyMediaFilmView(JsonableResponseMixin, UpdateView[Film, MyMediaFilmForm]):
    """Update Film via ajax request."""

    object: Film
    model = Film
    form_class = MyMediaFilmForm


class DeleteMyMediaBookView(DeleteMyMediaMixin, DeleteView[Book, ModelForm[Book]]):
    """Delete Book, add message, refresh MyMedia page."""

    object: Book
    model = Book


class DeleteMyMediaFilmView(DeleteMyMediaMixin, DeleteView[Film, ModelForm[Film]]):
    """Delete Film, add message, refresh MyMedia page."""

    object: Film
    model = Film
