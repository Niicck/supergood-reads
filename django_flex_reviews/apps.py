from django.apps import AppConfig

from .default_settings import apply_default_settings


class DjangoFlexReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_flex_reviews"

    def ready(self) -> None:
        apply_default_settings()
