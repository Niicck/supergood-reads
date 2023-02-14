import uuid
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Review(models.Model):
    """Entry Class for generating a User Review.

    Each Review can connect to:
        - 1 Media instance
        - 1 Strategy instance
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(default=timezone.now, null=False)
    completed_at_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)], blank=True, null=True
    )
    completed_at_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], blank=True, null=True
    )
    completed_at_year = models.IntegerField(blank=True, null=True)
    text = models.TextField(default="")

    # Allow reviews of any Strategy type
    strategy_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="strategy_review_set",
        blank=True,
        null=True,
    )
    strategy_object_id = models.PositiveIntegerField(blank=True, null=True)
    strategy = GenericForeignKey("strategy_content_type", "strategy_object_id")

    # Allow reviews of any Media type
    media_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name="media_review_set",
        blank=True,
        null=True,
    )
    media_object_id = models.PositiveIntegerField(blank=True, null=True)
    media = GenericForeignKey("media_content_type", "media_object_id")

    class Meta:
        ordering = (
            "-completed_at_year",
            "-completed_at_month",
            "-completed_at_day",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=["completed_at_year", "completed_at_month", "completed_at_day"],
                name="review_completed_at_idx",
            ),
            models.Index(fields=["strategy_content_type", "strategy_object_id"]),
            models.Index(fields=["media_content_type", "media_object_id"]),
        ]

    def __str__(self) -> str:
        return str(self.id)

    @property
    def completed_at(self) -> str:
        """Generate human-readable completed_at datestring."""
        if not self.completed_at_year:
            return ""
        elif not self.completed_at_month:
            return self.completed_at_year
        elif not self.completed_day:
            return datetime.strptime(
                self.completed_at_month + " " + self.completed_at_year, "%Y"
            ).strftime("%b %Y")
        else:
            return datetime.strptime(
                self.completed_at_day
                + " "
                + self.completed_at_month
                + " "
                + self.completed_at_year,
                "%d %m %Y",
            ).strftime("%d %b %Y")

    def validate_completed_at(self) -> None:
        """
        completed_at allows for approximate dates.
        Users are allowed to input:
            - a day, a month, and a year
            - just a month and a year
            - just a year
        Any other permutation is not allowed.
        """
        day = self.completed_at_day
        month = self.completed_at_month
        year = self.completed_at_year
        if day and month and year:
            try:
                datetime(year, month, day)
            except ValueError:
                raise ValidationError(
                    {
                        "completed_at_day": "Invalid date.",
                    }
                )
        if day and not month and not year:
            raise ValidationError(
                {
                    "completed_at_day": "Can't input a day without a month or year.",
                }
            )
        if day and month and not year:
            raise ValidationError(
                {
                    "completed_at_day": "Can't input a day without a year.",
                    "completed_at_month": "Can't input a month without a year.",
                }
            )
        if not day and month and not year:
            raise ValidationError(
                {
                    "completed_at_month": "Can't input a month without a year.",
                }
            )

    def clean(self) -> None:
        super().clean()
        self.validate_completed_at()

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        now = timezone.now()
        if self._state.adding:
            self.created_at = now
        self.updated_at = now
        super().save(*args, **kwargs)


class UserReviewStrategyDefault(models.Model):
    """Assign per-User default strategies for each Media type."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="media_user_default_set",
    )
    default_strategy = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="strategy_user_default_set",
    )

    def __str__(self) -> str:
        return str(self.id)
