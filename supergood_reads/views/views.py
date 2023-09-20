import logging
from functools import wraps
from typing import Any, Callable, Dict, Protocol, Type, TypeVar, cast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Model, Prefetch, Q, QuerySet
from django.forms import ModelForm
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
    QueryDict,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView
from rest_framework import generics, pagination, serializers, views
from rest_framework.request import Request
from rest_framework.response import Response

from supergood_reads.forms.media_item_forms import MediaItemFormGroup
from supergood_reads.forms.review_forms import InvalidContentTypeError, ReviewFormGroup
from supergood_reads.models import BaseMediaItem, Country, Genre, Review, UserSettings
from supergood_reads.models.media_items import (
    CountryMixin,
    GenreMixin,
    MediaItemQuerySet,
)
from supergood_reads.utils.content_type import (
    content_type_id_to_model,
    model_to_content_type_id,
)
from supergood_reads.utils.engine import supergood_reads_engine
from supergood_reads.utils.json import UUIDEncoder
from supergood_reads.utils.uuid import is_uuid
from supergood_reads.views.auth import (
    CreateMediaItemPermissionMixin,
    CreateReviewPermissionMixin,
    DeleteMediaPermissionMixin,
    DeleteReviewPermissionMixin,
    UpdateMediaItemPermissionMixin,
    UpdateReviewPermissionMixin,
)

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

        review_form_group = self.get_review_form_group()
        context_data = self._context_data_from_review_form_group(review_form_group)
        context.update(context_data)

        return context

    def get_review_form_group(self) -> ReviewFormGroup:
        return ReviewFormGroup(instance=self.object)

    def _context_data_from_review_form_group(
        self, review_form_group: ReviewFormGroup
    ) -> dict[str, Any]:
        context_data = {}

        # Forms
        review_form = review_form_group.review_form
        review_mgmt_form = review_form_group.review_mgmt_form
        strategy_forms_by_id = review_form_group.strategy_forms.by_content_type_id
        media_item_forms_by_id = review_form_group.media_item_forms.by_content_type_id
        context_data.update(
            {
                "review_form": review_form,
                "review_mgmt_form": review_mgmt_form,
                "strategy_forms_by_id": strategy_forms_by_id,
                "media_item_forms_by_id": media_item_forms_by_id,
            }
        )

        # Initial Values for Vue Components
        initial_strategy_content_type = review_form["strategy_content_type"].value()
        initial_media_item_content_type = review_form["media_item_content_type"].value()
        initial_media_item_object_id = review_form["media_item_object_id"].value()
        initial_create_new_media_item_object = review_mgmt_form[
            "create_new_media_item_object"
        ].value()

        context_data.update(
            {
                "initial_strategy_content_type": initial_strategy_content_type,
                "initial_media_item_content_type": initial_media_item_content_type,
                "initial_media_item_object_id": initial_media_item_object_id,
                "initial_create_new_media_item_object": initial_create_new_media_item_object,
            }
        )

        # Initial Data for Vue Store
        initial_data_for_vue_store = {
            "selectedStrategyContentType": initial_strategy_content_type,
            "selectedMediaItemContentType": initial_media_item_content_type,
            "selectedMediaItemObjectId": initial_media_item_object_id,
            "createNewMediaItemObject": initial_create_new_media_item_object,
            "autocompleteUrlBase": reverse("media_item_autocomplete"),
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

        assert isinstance(review.media_item, BaseMediaItem)
        messages.success(request, f"Added review for {review.media_item.title}.")
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

    def get_review_form_group(self) -> ReviewFormGroup:
        initial = {}
        base_media_item_id = self.request.GET.get("base-media-item-id", None)
        if base_media_item_id:
            try:
                media_item = BaseMediaItem.objects.get(id=base_media_item_id)
                child = media_item.get_child()
                if child:
                    initial = {
                        "review_form": {
                            "media_item_object_id": child.id,
                            "media_item_content_type": model_to_content_type_id(child),
                        }
                    }
            except BaseMediaItem.DoesNotExist:
                pass

        review_form_group = ReviewFormGroup(initial=initial)
        return review_form_group


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
        if self.object.media_item:
            title = self.object.media_item.title
        else:
            title = "untitled"
        messages.success(self.request, f"Succesfully deleted review of '{title}'.")
        return super().form_valid(form)  # type: ignore[safe-super]


class MediaItemAutocompleteView(View):
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
            if not (model_class and issubclass(model_class, BaseMediaItem)):
                raise InvalidContentTypeError
        except (ContentType.DoesNotExist, InvalidContentTypeError, ValueError):
            return JsonResponse(
                {"error": f"Invalid content type ID {content_type_id}"}, status=400
            )

        manager = cast(MediaItemQuerySet[BaseMediaItem], model_class.objects)

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
    def to_representation(self, obj: BaseMediaItem) -> dict[str, Any]:
        return {
            "id": model_to_content_type_id(obj),
            "name": obj._meta.verbose_name,
        }


class MediaTypeChoicesApiView(views.APIView):
    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        media_item_options = supergood_reads_engine.media_item_model_classes
        serializer = MediaTypeOptionSerializer(
            media_item_options, many=True
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


class BaseMediaItemSerializer(serializers.Serializer):
    def to_representation(self, base: BaseMediaItem) -> dict[str, Any]:
        user = self.context["request"].user
        update_url: str | None = None
        media_item = base.get_child()

        genres: list[str] = []
        if issubclass(media_item.__class__, GenreMixin):  # type: ignore
            genres = list(media_item.genres.all().values_list("name", flat=True))  # type: ignore

        if media_item.can_user_change(user):
            update_url = reverse("update_media_item", args=[base.id])

        base_review_url = reverse("create_review")
        review_query_params = QueryDict(mutable=True)
        review_query_params["base-media-item-id"] = str(base.id)
        review_url = f"{base_review_url}?{review_query_params.urlencode()}"

        return {
            "id": media_item.id,
            "title": media_item.title,
            "year": media_item.year,
            "creator": media_item.creator,
            "genres": genres,
            "icon": media_item.icon(),
            "updateUrl": update_url,
            "reviewUrl": review_url,
        }


class MediaItemSearchView(generics.ListAPIView):
    serializer_class = BaseMediaItemSerializer
    pagination_class = SupergoodPagination
    qs: QuerySet[BaseMediaItem]

    def get_queryset(self) -> QuerySet[BaseMediaItem]:
        self.parse_query_params()
        self.set_searchable_media_types()
        self.set_qs()
        self.apply_genre_filter()
        self.apply_user_filter()
        self.qs = self.qs.filter(title__icontains=self.q)
        self.qs = self.qs.order_by("-updated_at")
        return self.qs.distinct()

    def parse_query_params(self) -> None:
        query_params = self.request.query_params
        self.q = query_params.get("q", "").strip()
        self.my_media_only = query_params.get("myMediaOnly", "false") == "true"
        self.genres = query_params.getlist("genres")
        self.media_type_ids = query_params.getlist("mediaTypes")

    def set_searchable_media_types(self) -> None:
        media_types = [content_type_id_to_model(m_id) for m_id in self.media_type_ids]
        self.searchable_media_types: list[Type[BaseMediaItem]] = [
            m for m in self.all_media_types if m in media_types
        ]
        if self.genres:
            self.searchable_media_types = list(
                set(self.media_types_with_genres) & set(self.searchable_media_types)
            )

    def set_qs(self) -> None:
        if not self.searchable_media_types:
            self.qs = BaseMediaItem.objects.none()

        # select_related media_types
        select_related_args = [
            media_type.__name__.lower() for media_type in self.searchable_media_types
        ]
        self.qs = BaseMediaItem.objects.select_related(*select_related_args)

        # filter for BaseMediaItems where selected media_types are not null
        media_type_filter = Q()
        for media_type in self.searchable_media_types:
            non_null_media_type_filter = Q(
                **{f"{media_type.__name__.lower()}__isnull": False}
            )
            media_type_filter |= non_null_media_type_filter
        self.qs = self.qs.filter(media_type_filter)

    def apply_genre_filter(self) -> None:
        if not self.genres:
            return

        # prefetch our genres
        prefetch_genres = [
            Prefetch(f"{m.__name__.lower()}__genres")
            for m in self.searchable_media_types
        ]
        self.qs = self.qs.prefetch_related(*prefetch_genres)

        # filter by genre
        genre_filter = Q()
        for media_type in self.searchable_media_types:
            genre_filter |= Q(
                **{f"{media_type.__name__.lower()}__genres__name__in": self.genres}
            )
        self.qs = self.qs.filter(genre_filter)

    def apply_user_filter(self) -> None:
        owner_filter = Q(owner=self.request.user)
        validated_filter = Q(validated=True)

        if self.my_media_only:
            if self.request.user.is_authenticated:
                self.qs = self.qs.filter(owner_filter)
            else:
                self.qs = BaseMediaItem.objects.none()
        else:
            if self.request.user.is_authenticated:
                self.qs = self.qs.filter(validated_filter | owner_filter)
            else:
                self.qs = self.qs.filter(validated_filter)

    @property
    def all_media_types(self) -> list[type[BaseMediaItem]]:
        return supergood_reads_engine.media_item_model_classes

    @property
    def media_types_with_genres(self) -> list[type[BaseMediaItem]]:
        return self._media_types_with_mixin(GenreMixin)

    @property
    def media_types_with_countries(self) -> list[type[BaseMediaItem]]:
        return self._media_types_with_mixin(CountryMixin)

    def _media_types_with_mixin(self, mixin: type[Model]) -> list[type[BaseMediaItem]]:
        return [
            m
            for m in supergood_reads_engine.media_item_model_classes
            if issubclass(m, mixin)
        ]


class LibraryView(TemplateView):
    template_name = "supergood_reads/views/library.html"


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
            qs = all_reviews_qs.filter(validated=True)
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
    object: BaseMediaItem | None = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        media_item_form_group = MediaItemFormGroup(instance=self.object)
        context_data = self._context_data_from_form_group(media_item_form_group)
        context.update(context_data)

        return context

    def _context_data_from_form_group(
        self, media_item_form_group: MediaItemFormGroup
    ) -> dict[str, Any]:
        context_data = {}

        media_item_forms_by_id = (
            media_item_form_group.media_item_forms.by_content_type_id
        )
        media_mgmt_form = media_item_form_group.media_mgmt_form
        initial_media_item_content_type = media_mgmt_form[
            "media_item_content_type"
        ].value()

        context_data.update(
            {
                "media_item_forms_by_id": media_item_forms_by_id,
                "media_mgmt_form": media_mgmt_form,
                "initial_data_for_vue_store": {
                    "selectedMediaItemContentType": initial_media_item_content_type,
                },
            }
        )
        return context_data

    @transaction.atomic
    @log_post_request_data
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        media_item_form_group = MediaItemFormGroup(
            data=request.POST, instance=self.object, user=cast(User, self.request.user)
        )
        if not media_item_form_group.is_valid():
            messages.error(request, "Please fix the errors below.")
            return self.on_form_error(request, media_item_form_group, status_code=400)

        try:
            media_item = media_item_form_group.save()
        except Exception:
            logger.exception("Failed to create Media Item")
            messages.error(request, "Server Error.")
            return self.on_form_error(request, media_item_form_group, status_code=500)

        messages.success(request, f'Saved "{media_item.title}"')
        return self.redirect_to_library()

    def on_form_error(
        self,
        request: HttpRequest,
        media_item_form_group: MediaItemFormGroup,
        status_code: int = 500,
    ) -> HttpResponse:
        context = super().get_context_data()
        context_data = self._context_data_from_form_group(media_item_form_group)
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
    template_name = "supergood_reads/views/media_item_form/create_media_item.html"


class UpdateMediaItemView(
    UpdateMediaItemPermissionMixin, MediaFormView, SingleObjectMixin[BaseMediaItem]
):
    template_name = "supergood_reads/views/media_item_form/update_media_item.html"
    model = BaseMediaItem

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        try:
            # TODO: replace BaseMediaItem with MediaItem
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, "Invalid Request.")
            return self.redirect_to_library()
        return super().dispatch(request, *args, **kwargs)

    def get_object(
        self, queryset: QuerySet[BaseMediaItem] | None = None
    ) -> BaseMediaItem:
        object = super().get_object(queryset)
        child = object.get_child()
        if not child:
            raise Http404
        return child


class DeleteMediaItemView(
    DeleteMediaPermissionMixin,
    DeleteView[BaseMediaItem, ModelForm[BaseMediaItem]],
):
    """Delete Media Item, add message, refresh Library page."""

    object: BaseMediaItem
    model = BaseMediaItem

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
        self, queryset: QuerySet[BaseMediaItem] | None = None
    ) -> BaseMediaItem:
        object = super().get_object(queryset)
        child = object.get_child()
        if not child:
            raise Http404
        return child


class UserSettingsView(LoginRequiredMixin, DetailView[UserSettings]):
    template_name = "supergood_reads/views/user_settings.html"

    def get_object(
        self, queryset: QuerySet[UserSettings] | None = None
    ) -> UserSettings:
        user_settings, created = UserSettings.objects.get_or_create(
            user=self.request.user
        )
        return user_settings


class DeleteUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            logout(request)
            user.delete()
            return HttpResponseRedirect(reverse("home"))
        except Exception:
            logger.exception("Failed to delete User.")
            messages.error(request, "An unexpected error occurred. Please try again.")
            return HttpResponseRedirect(reverse("user_settings"))
