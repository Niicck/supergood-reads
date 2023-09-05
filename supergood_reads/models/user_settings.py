from django.conf import settings
from django.db import models

from supergood_reads.models.media_items import BaseMediaItem
from supergood_reads.models.review import Review


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, required=True, db_index=True
    )
    review_limit = models.IntegerField(null=True, blank=True, default=100)
    media_item_limit = models.IntegerField(null=True, blank=True, default=100)

    def __str__(self) -> str:
        return str(self.user.id)

    @property
    def review_count(self) -> int:
        return Review.objects.filter(owner=self.user).count()

    @property
    def media_item_count(self) -> int:
        return BaseMediaItem.objects.filter(owner=self.user).count()

    @property
    def reviews_remaining(self) -> str:
        if self.review_limit is None:
            return "Unlimited"
        return str(self.review_limit - self.review_count)

    @property
    def media_items_remaining(self) -> str:
        if self.media_item_limit is None:
            return "Unlimited"
        return str(self.media_item_limit - self.media_item_count)

    @property
    def can_create_review(self) -> bool:
        if self.review_limit is None:
            return True
        return self.review_count <= self.review_limit

    @property
    def can_create_media_item(self) -> bool:
        if self.media_item_limit is None:
            return True
        return self.media_item_count <= self.media_item_limit

    class Meta:
        verbose_name_plural = "User Settings"
