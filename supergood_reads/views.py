import logging
from functools import wraps
from typing import Any, Callable, Dict, Protocol, TypeVar

from django.conf import settings
from django.contrib import messages
from django.db.models import CharField, QuerySet, Value
from django.db.models.functions import Concat
from django.forms import ModelForm
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView
from queryset_sequence import QuerySetSequence

from supergood_reads.auth import (
    CreateReviewPermissionMixin,
    DeleteMediaPermissionMixin,
    DeleteReviewPermissionMixin,
    UpdateMediaPermissionMixin,
    UpdateReviewPermissionMixin,
)
from supergood_reads.media_types.forms import MyMediaBookForm, MyMediaFilmForm
from supergood_reads.media_types.models import AbstractMediaType, Book, Film
from supergood_reads.reviews.forms import ReviewFormGroup
from supergood_reads.reviews.models import Review
from supergood_reads.utils.json import UUIDEncoder
from supergood_reads.utils.uuid import is_uuid

logger = logging.getLogger(__name__)

ViewType = TypeVar("ViewType", bound="View")


def log_post_request_data(
    view_func: Callable[[ViewType, HttpRequest, Any, Any], Any]
) -> Callable[[ViewType, HttpRequest, Any, Any], Any]:
    @wraps(view_func)
    def _wrapped_view_method(
        self: ViewType, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Any:
        if settings.DEBUG:
            request_data = dict(request.POST.items())
            logger.info(request_data)
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view_method


class ReviewFormView(TemplateView):
    object: Review | None = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        review_form_group = ReviewFormGroup(instance=self.object)
        context["review_form"] = review_form_group.review_form
        context["review_mgmt_form"] = review_form_group.review_mgmt_form
        context["strategy_forms"] = review_form_group.strategy_forms.by_content_type_id
        context[
            "media_type_forms"
        ] = review_form_group.media_type_forms.by_content_type_id

        return context

    @log_post_request_data
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        review_form_group = ReviewFormGroup(data=request.POST, instance=self.object)
        if not review_form_group.is_valid():
            messages.error(request, "Please fix the errors below.")
            return self.on_form_error(request, review_form_group, status_code=400)

        try:
            review = review_form_group.save()
        except Exception:
            logger.exception("Failed to create Review")
            messages.error(request, "Server Error.")
            return self.on_form_error(request, review_form_group, status_code=500)

        assert isinstance(review.media_type, AbstractMediaType)
        messages.success(request, f"Added review for {review.media_type.title}.")
        return self.redirect_to_reviews()

    def on_form_error(
        self,
        request: HttpRequest,
        review_form_group: ReviewFormGroup,
        status_code: int = 500,
    ) -> HttpResponse:
        return render(
            request,
            self.template_name,
            {
                "review_form": review_form_group.review_form,
                "review_mgmt_form": review_form_group.review_mgmt_form,
                "strategy_forms": review_form_group.strategy_forms.by_content_type_id,
                "media_type_forms": review_form_group.media_type_forms.by_content_type_id,
            },
            status=status_code,
        )

    def redirect_to_reviews(
        self,
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        return redirect("reviews")


class CreateReviewView(CreateReviewPermissionMixin, ReviewFormView):
    template_name = "supergood_reads/create_review.html"


class UpdateReviewView(
    UpdateReviewPermissionMixin, ReviewFormView, SingleObjectMixin[Review]
):
    template_name = "supergood_reads/update_review.html"
    model = Review

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, "Invalid Request.")
            return self.redirect_to_reviews()
        return super().dispatch(request, *args, **kwargs)


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


class DeleteReview(DeleteReviewPermissionMixin, DeleteView[Review, ModelForm[Review]]):
    """Delete Film, add message, refresh Reviews page."""

    object: Review
    model = Review

    def get_success_url(self: FormViewMixinProtocol) -> str:
        return reverse("reviews")

    def form_invalid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        messages.error(self.request, "Please fix the errors below.")
        return super().form_invalid(form)  # type: ignore[safe-super]

    def form_valid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        if self.object.media_type:
            title = self.object.media_type.title
        else:
            title = "untitled"
        messages.success(self.request, f"Succesfully deleted review of '{title}'.")
        return super().form_valid(form)  # type: ignore[safe-super]


class FilmAutocompleteView(View):
    limit = 20

    def get(self, request: HttpRequest) -> JsonResponse:
        query_dict = request.GET
        q = query_dict.get("q", "")
        if is_uuid(q):
            film_qs = Film.objects.filter(pk=q)
        else:
            film_qs = Film.objects.filter(title__icontains=q)
        films = film_qs.annotate(
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
        if is_uuid(q):
            book_qs = Book.objects.filter(pk=q)
        else:
            book_qs = Book.objects.filter(title__icontains=q)
        books = book_qs.annotate(
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
    template_name = "supergood_reads/media.html"

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
    template_name = "supergood_reads/reviews.html"

    def get_queryset(self) -> QuerySet[Review]:
        review_qs = (
            Review.objects.with_generic_relations()
            .all()
            .order_by("-completed_at_year", "-completed_at_month", "-completed_at_day")
        )
        return review_qs


class JsonableResponseMixin:
    """
    Mixin to add JSON response support to a form.
    Must be used with an object-based FormView (e.g. CreateView, UpdateView)
    """

    def form_invalid(self, form: ModelForm[Any]) -> JsonResponse:
        return JsonResponse({"fieldErrors": form.errors}, status=400)

    def form_valid(self, form: ModelForm[Any]) -> JsonResponse:
        self.object = form.save()
        data = {
            "id": self.object.pk,
            **{field: getattr(self.object, field) for field in form.fields},
        }
        return JsonResponse({"data": data})


class DeleteMyMediaMixin:
    def get_success_url(self: FormViewMixinProtocol) -> str:
        return reverse("media")

    def form_invalid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        messages.error(self.request, "Please fix the errors below.")
        return super().form_invalid(form)  # type: ignore[safe-super]

    def form_valid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        title = self.object.title
        messages.success(self.request, f"Succesfully deleted {title}.")
        return super().form_valid(form)  # type: ignore[safe-super]


class UpdateMyMediaBookView(
    UpdateMediaPermissionMixin, JsonableResponseMixin, UpdateView[Book, MyMediaBookForm]
):
    """Update Book via ajax request."""

    object: Book
    model = Book
    form_class = MyMediaBookForm


class UpdateMyMediaFilmView(
    UpdateMediaPermissionMixin, JsonableResponseMixin, UpdateView[Film, MyMediaFilmForm]
):
    """Update Film via ajax request."""

    object: Film
    model = Film
    form_class = MyMediaFilmForm


class DeleteMyMediaBookView(
    DeleteMediaPermissionMixin, DeleteMyMediaMixin, DeleteView[Book, ModelForm[Book]]
):
    """Delete Book, add message, refresh MyMedia page."""

    object: Book
    model = Book


class DeleteMyMediaFilmView(
    DeleteMediaPermissionMixin, DeleteMyMediaMixin, DeleteView[Film, ModelForm[Film]]
):
    """Delete Film, add message, refresh MyMedia page."""

    object: Film
    model = Film


class LoginView(TemplateView):
    template_name = "supergood_reads/login.html"


class StatusTemplateView(TemplateView):
    status = 200

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=self.status)


class Handle403View(StatusTemplateView):
    template_name = "supergood_reads/403.html"
    status = 403

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        return self.get(request, *args, **kwargs)
