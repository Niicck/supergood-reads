import logging
from functools import wraps
from typing import Any, Callable, Dict, Protocol, Type, TypeVar, cast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Q, QuerySet
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
from django.views.generic.edit import DeleteView
from queryset_sequence import QuerySetSequence
from rest_framework import generics, pagination, serializers, views
from rest_framework.request import Request
from rest_framework.response import Response

from supergood_reads.auth import (
    CreateMediaItemPermissionMixin,
    CreateReviewPermissionMixin,
    DeleteMediaPermissionMixin,
    DeleteReviewPermissionMixin,
    UpdateMediaItemPermissionMixin,
    UpdateReviewPermissionMixin,
)
from supergood_reads.media_types.forms import MediaTypeFormGroup
from supergood_reads.media_types.models import (
    AbstractMediaType,
    Book,
    Country,
    Film,
    Genre,
    MediaTypeQuerySet,
)
from supergood_reads.reviews.forms import InvalidContentTypeError, ReviewFormGroup
from supergood_reads.reviews.models import Review
from supergood_reads.utils import ContentTypeUtils
from supergood_reads.utils.engine import supergood_reads_engine
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
        context_data = self._context_data_from_review_form_group(review_form_group)
        context.update(context_data)

        return context

    def _context_data_from_review_form_group(
        self, review_form_group: ReviewFormGroup
    ) -> dict[str, Any]:
        context_data = {}

        # Forms
        review_form = review_form_group.review_form
        review_mgmt_form = review_form_group.review_mgmt_form
        strategy_forms_by_id = review_form_group.strategy_forms.by_content_type_id
        media_type_forms_by_id = review_form_group.media_type_forms.by_content_type_id
        context_data.update(
            {
                "review_form": review_form,
                "review_mgmt_form": review_mgmt_form,
                "strategy_forms_by_id": strategy_forms_by_id,
                "media_type_forms_by_id": media_type_forms_by_id,
            }
        )

        # Initial Values for Vue Components
        initial_strategy_content_type = review_form["strategy_content_type"].value()
        initial_media_type_content_type = review_form["media_type_content_type"].value()
        initial_media_type_object_id = review_form["media_type_object_id"].value()
        initial_create_new_media_type_object = review_mgmt_form[
            "create_new_media_type_object"
        ].value()

        context_data.update(
            {
                "initial_strategy_content_type": initial_strategy_content_type,
                "initial_media_type_content_type": initial_media_type_content_type,
                "initial_media_type_object_id": initial_media_type_object_id,
                "initial_create_new_media_type_object": initial_create_new_media_type_object,
            }
        )

        # Initial Data for Vue Store
        initial_data_for_vue_store = {
            "selectedStrategyId": initial_strategy_content_type,
            "selectedMediaTypeContentType": initial_media_type_content_type,
            "selectedMediaTypeObjectId": initial_media_type_object_id,
            "createNewMediaTypeObject": initial_create_new_media_type_object,
            "autocompleteUrlBase": reverse("media_type_autocomplete"),
        }
        context_data.update(
            {
                "initial_data_for_vue_store": initial_data_for_vue_store,
            }
        )

        return context_data

    @transaction.atomic
    @log_post_request_data
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        review_form_group = ReviewFormGroup(
            data=request.POST, instance=self.object, user=cast(User, self.request.user)
        )
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
        context_data = self._context_data_from_review_form_group(review_form_group)
        return render(
            request,
            self.template_name,
            context_data,
            status=status_code,
        )

    def redirect_to_reviews(
        self,
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        return redirect("reviews")


class CreateReviewView(CreateReviewPermissionMixin, ReviewFormView):
    template_name = "supergood_reads/views/review_form/create_review.html"


class UpdateReviewView(
    UpdateReviewPermissionMixin, ReviewFormView, SingleObjectMixin[Review]
):
    template_name = "supergood_reads/views/review_form/update_review.html"
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

    def get_success_url(self) -> str:
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


class MediaTypeAutocompleteView(View):
    limit = 20

    def get(self, request: HttpRequest) -> JsonResponse:
        query_dict = request.GET
        content_type_id = query_dict.get("content_type_id", "")
        q = query_dict.get("q", "").strip()

        try:
            if not content_type_id:
                raise InvalidContentTypeError
            content_type = ContentType.objects.get_for_id(int(content_type_id))
            model_class = content_type.model_class()
            if not (model_class and issubclass(model_class, AbstractMediaType)):
                raise InvalidContentTypeError
        except (ContentType.DoesNotExist, InvalidContentTypeError, ValueError):
            return JsonResponse(
                {"error": f"Invalid content type ID {content_type_id}"}, status=400
            )

        manager = cast(MediaTypeQuerySet[AbstractMediaType], model_class.objects)

        if is_uuid(q):
            qs = manager.filter(pk=q)
        else:
            qs = manager.filter(title__icontains=q, validated=True)
        qs = qs.with_autocomplete_label()[: self.limit]
        values = qs.values("id", "title", "autocomplete_label")  # type: ignore[misc]

        return JsonResponse(
            {
                "results": list(values),
            },
            encoder=UUIDEncoder,
        )


class SupergoodPagination(pagination.PageNumberPagination):
    page_query_param = "page"
    page_size = 40

    def get_page_number(self, request: Request, paginator: Paginator[Any]) -> int:
        try:
            return int(super().get_page_number(request, paginator))
        except EmptyPage:
            return 1

    def get_paginated_response(self, data: Any) -> Response:
        has_next = self.page.has_next()
        has_previous = self.page.has_previous()
        next_page_number = self.page.next_page_number() if has_next else None
        previous_page_number = (
            self.page.previous_page_number() if has_previous else None
        )
        return Response(
            {
                "pagination": {
                    "hasNext": has_next,
                    "hasPrevious": has_previous,
                    "nextPageNumber": next_page_number,
                    "previousPageNumber": previous_page_number,
                    "startIndex": self.page.start_index(),
                    "endIndex": self.page.end_index(),
                    "count": self.page.paginator.count,
                },
                "results": data,
            }
        )


class MediaTypeOptionSerializer(serializers.BaseSerializer):
    def to_representation(self, obj: AbstractMediaType) -> dict[str, Any]:
        return {
            "id": ContentTypeUtils().get_content_type_id(obj),
            "name": obj._meta.verbose_name,
        }


class MediaTypeChoicesApiView(views.APIView):
    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        media_type_options = supergood_reads_engine.media_type_model_classes
        serializer = MediaTypeOptionSerializer(
            media_type_options, many=True
        )  # Serialize the list
        return Response(serializer.data)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class GenreApiView(generics.ListAPIView):
    serializer_class = GenreSerializer

    def get_queryset(self) -> QuerySet[Genre]:
        return Genre.objects.all().order_by("name")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["name"]


class CountryApiView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self) -> QuerySet[Country]:
        return Country.objects.all().order_by("name")


class MediaTypeSerializer(serializers.BaseSerializer):
    """DRF Serializers don't work with Abstract Model Classes."""

    def to_representation(self, obj: AbstractMediaType) -> dict[str, Any]:
        user = self.context["request"].user
        update_url: str | None = None
        if obj.can_user_change(user):
            update_url = reverse("update_media_item", args=[obj.id])

        return {
            "id": obj.id,
            "title": obj.title,
            "year": obj.year,
            "creator": obj.creator,
            "genres": list(obj.genres.all().values_list("name", flat=True)),
            "icon": obj.icon(),
            "updateUrl": update_url,
        }


class MediaTypeSearchView(generics.ListAPIView):
    serializer_class = MediaTypeSerializer
    pagination_class = SupergoodPagination

    def get_queryset(self) -> QuerySetSequence:
        query_params = self.request.query_params
        q = query_params.get("q", "").strip()
        editable_only = query_params.get("showEditableOnly", "false") == "true"
        genres = query_params.getlist("genres")
        media_type_ids = query_params.getlist("media_types")

        media_type_models = [
            ContentTypeUtils().get_model(m_id) for m_id in media_type_ids
        ]
        searchable_media_types = [
            m for m in self.all_media_types if m in media_type_models
        ]
        if genres:
            searchable_media_types = list(
                set(self.media_types_with_genres) & set(searchable_media_types)
            )

        if editable_only:
            qs = self._editable_qs(searchable_media_types)
        else:
            qs = self._qs_for_media_types(searchable_media_types).filter(
                Q(validated=True) | Q(owner=self.request.user)
            )

        qs.prefetch_related("genres")

        if is_uuid(q):
            qs = qs.filter(pk=q)
        else:
            qs = qs.filter(title__icontains=q)

        if genres:
            qs = qs.filter(genres__name__in=genres)

        qs = qs.order_by("-updated_at")
        return qs

    @property
    def all_media_types(self) -> list[type[AbstractMediaType]]:
        return supergood_reads_engine.media_type_model_classes

    @property
    def media_types_with_genres(self) -> list[type[AbstractMediaType]]:
        return self._media_types_with_field("genres")

    @property
    def media_types_with_countries(self) -> list[type[AbstractMediaType]]:
        return self._media_types_with_field("countries")

    def _media_types_with_field(self, field_name: str) -> list[type[AbstractMediaType]]:
        return [
            m
            for m in supergood_reads_engine.media_type_model_classes
            if field_name in [f.name for f in m._meta.get_fields()]
        ]

    def _editable_qs(
        self, searchable_media_types: list[type[AbstractMediaType]]
    ) -> QuerySetSequence:
        """
        Return queryset combining all child content_types of AbstractMediaType.
        Ex: by default, this will return both Books and Films, ordered by "updated_at"
        in descending order.
        """
        user = self.request.user
        if user.is_staff:
            editable_media_types = [
                mt for mt in self.all_media_types if mt().can_user_change(user)
            ]
            searchable_media_types = list(
                set(editable_media_types) & set(searchable_media_types)
            )
            qs = self._qs_for_media_types(searchable_media_types)
        elif user.is_authenticated:
            all_media_types_qs = self._qs_for_media_types(searchable_media_types)
            qs = all_media_types_qs.filter(owner=self.request.user)
        else:
            qs = Book.objects.none()
        return qs

    def _qs_for_media_types(
        self, media_types: list[Type[AbstractMediaType]]
    ) -> QuerySetSequence:
        return QuerySetSequence(
            *[media_type.objects.all() for media_type in media_types],
            model=AbstractMediaType,
        )


class LibraryView(TemplateView):
    template_name = "supergood_reads/views/library/library.html"


class MyReviewsView(ListView[Review]):
    model = Review
    paginate_by = 20
    context_object_name = "review_list"
    template_name = "supergood_reads/views/review_list/review_list.html"

    def get_queryset(self) -> QuerySet[Review]:
        user = self.request.user
        all_reviews_qs = (
            Review.objects.all()
            .with_generic_relations()
            .order_by("-completed_at_year", "-completed_at_month", "-completed_at_day")
        )
        if user.has_perm("supergood_reads.change_review"):
            qs = all_reviews_qs
        elif user.is_authenticated:
            qs = all_reviews_qs.filter(owner=self.request.user)
        else:
            qs = all_reviews_qs.filter(demo=True)
        return qs


class StatusTemplateView(TemplateView):
    status = 200

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=self.status)


class Handle403View(StatusTemplateView):
    template_name = "supergood_reads/views/403.html"
    status = 403

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        return self.get(request, *args, **kwargs)


class MediaFormView(TemplateView):
    object: AbstractMediaType | None = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        media_type_form_group = MediaTypeFormGroup(instance=self.object)
        context_data = self._context_data_from_form_group(media_type_form_group)
        context.update(context_data)

        return context

    def _context_data_from_form_group(
        self, media_type_form_group: MediaTypeFormGroup
    ) -> dict[str, Any]:
        context_data = {}

        media_type_forms_by_id = (
            media_type_form_group.media_type_forms.by_content_type_id
        )
        media_mgmt_form = media_type_form_group.media_mgmt_form
        initial_media_type_content_type = media_mgmt_form[
            "media_type_content_type"
        ].value()

        context_data.update(
            {
                "media_type_forms_by_id": media_type_forms_by_id,
                "media_mgmt_form": media_mgmt_form,
                "initial_data_for_vue_store": {
                    "selectedMediaTypeContentType": initial_media_type_content_type,
                },
            }
        )
        return context_data

    @transaction.atomic
    @log_post_request_data
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        media_type_form_group = MediaTypeFormGroup(
            data=request.POST, instance=self.object, user=cast(User, self.request.user)
        )
        if not media_type_form_group.is_valid():
            messages.error(request, "Please fix the errors below.")
            return self.on_form_error(request, media_type_form_group, status_code=400)

        try:
            media_item = media_type_form_group.save()
        except Exception:
            logger.exception("Failed to create Media Item")
            messages.error(request, "Server Error.")
            return self.on_form_error(request, media_type_form_group, status_code=500)

        messages.success(request, f'Saved "{media_item.title}"')
        return self.redirect_to_library()

    def on_form_error(
        self,
        request: HttpRequest,
        media_type_form_group: MediaTypeFormGroup,
        status_code: int = 500,
    ) -> HttpResponse:
        context = super().get_context_data()
        context_data = self._context_data_from_form_group(media_type_form_group)
        context.update(context_data)
        return render(
            request,
            self.template_name,
            context,
            status=status_code,
        )

    def redirect_to_library(
        self,
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        return redirect("library")


class CreateMediaItemView(CreateMediaItemPermissionMixin, MediaFormView):
    template_name = "supergood_reads/views/media_type_form/create_media_type.html"


class UpdateMediaItemView(
    UpdateMediaItemPermissionMixin, MediaFormView, SingleObjectMixin[AbstractMediaType]
):
    template_name = "supergood_reads/views/media_type_form/update_media_type.html"
    model = AbstractMediaType

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        try:
            # TODO: replace AbstractMediaType with MediaItem
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, "Invalid Request.")
            return self.redirect_to_library()
        return super().dispatch(request, *args, **kwargs)

    def get_object(
        self, queryset: QuerySet[AbstractMediaType] | None = None
    ) -> AbstractMediaType:
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            object: AbstractMediaType = QuerySetSequence(
                Book.objects.all(), Film.objects.all(), model=AbstractMediaType
            ).get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        return object


class DeleteMediaItemView(
    DeleteMediaPermissionMixin,
    DeleteView[AbstractMediaType, ModelForm[AbstractMediaType]],
):
    """Delete Media Item, add message, refresh Library page."""

    object: AbstractMediaType
    model = AbstractMediaType

    def get_success_url(self: FormViewMixinProtocol) -> str:
        return reverse("library")

    def form_invalid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        messages.error(self.request, "Please fix the errors below.")
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def form_valid(
        self: FormViewMixinProtocol, form: ModelForm[Any]
    ) -> HttpResponseRedirect:
        user = self.request.user

        if self.object.reviews.exclude(Q(owner=user) | Q(owner__isnull=True)).exists():
            messages.error(
                self.request,
                f'Other people have made Reviews for "{self.object.title}", '
                "so you can't delete it.",
            )
            return HttpResponseRedirect(self.get_success_url())

        self.object.reviews.all().delete()
        messages.success(self.request, f"Succesfully deleted {self.object.title}.")
        return super().form_valid(form)  # type: ignore[safe-super]

    def get_object(
        self, queryset: QuerySet[AbstractMediaType] | None = None
    ) -> AbstractMediaType:
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            object: AbstractMediaType = QuerySetSequence(
                Book.objects.all(), Film.objects.all(), model=AbstractMediaType
            ).get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        return object
