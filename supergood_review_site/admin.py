from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from supergood_review_site.reviews.forms import ReviewForm
from supergood_review_site.reviews.models import Review


class ReviewAdmin(admin.ModelAdmin[Review]):
    list_display = ("media", "view_completed_at")
    form = ReviewForm

    @admin.display
    def view_completed_at(self, obj: Review) -> str:
        return obj.completed_at

    def get_queryset(self, request: HttpRequest) -> models.QuerySet[Review]:
        queryset = super().get_queryset(request)
        return queryset
