from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from supergood_reads.forms.review_forms import ReviewForm
from supergood_reads.models import Review, UserSettings


class ReviewAdmin(admin.ModelAdmin[Review]):
    list_display = ("media_item", "view_completed_at")
    form = ReviewForm

    @admin.display
    def view_completed_at(self, obj: Review) -> str:
        return obj.completed_at

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[Review]:
        queryset = super().get_queryset(request)
        return queryset


class UserSettingsAdmin(admin.ModelAdmin[UserSettings]):
    list_display = (
        "user",
        "review_count",
        "reviews_remaining",
        "media_item_count",
        "media_items_remaining",
    )
    fields = [
        "user",
        "review_count",
        "reviews_remaining",
        "review_limit",
        "media_item_count",
        "media_items_remaining",
        "media_item_limit",
    ]
    readonly_fields = [
        "user",
        "review_count",
        "media_item_count",
        "reviews_remaining",
        "media_items_remaining",
    ]

    def review_count(self, obj: UserSettings) -> int:
        return obj.review_count

    def media_item_count(self, obj: UserSettings) -> int:
        return obj.media_item_count

    def reviews_remaining(self, obj: UserSettings) -> str:
        return obj.reviews_remaining

    def media_items_remaining(self, obj: UserSettings) -> str:
        return obj.media_items_remaining
