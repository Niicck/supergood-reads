from typing import Any, Optional, Type, final

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.forms import ModelForm
from django.utils.module_loading import import_string

from supergood_reads.media_types.forms import BookAutocompleteForm, FilmAutocompleteForm
from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.models import Book, Review
from supergood_reads.strategies.forms import (
    EbertStrategyForm,
    GoodreadsStrategyForm,
    MaximusStrategyForm,
)
from supergood_reads.strategies.models import AbstractStrategy

SUPERGOOD_READS_CONFIG = "SUPERGOOD_READS_CONFIG"


class InvalidSupergoodReadsConfigError(ImproperlyConfigured):
    pass


class SupergoodReadsConfig:
    """
    Base configuration class for a supergood_reads application.
    You can subclass this to provide custom configurations for your own application.

    These variables and methods can be overwritten in a subclass:
        strategy_form_classes
        media_type_form_classes
        demo_review_queryset
        demo_media_queryset
    """

    """
    Strategies that are eligible to be selected when creating a new Review.
    Users can override this variable in a subclass to return their own strategies.
    """
    strategy_form_classes: list[Type[ModelForm[Any]]] = []

    """
    MediaTypes are eligible to be selected when creating a new Review.
    Users can override this variable in a subclass to return their own media_types.
    """
    media_type_form_classes: list[Type[ModelForm[Any]]] = []

    def __init__(self) -> None:
        self._validate_strategy_form_classes()
        self._validate_media_type_form_classes()

    def _validate_strategy_form_classes(self) -> None:
        """Validate that all strategy_form_classes are Strategies."""
        for form_class in self.strategy_form_classes:
            if not isinstance(form_class, type):
                raise InvalidSupergoodReadsConfigError(
                    "Expected an uninstantiated form class, but got an instance: "
                    f"{form_class}. Please ensure strategy_form_classes and "
                    "media_type_form_classes in your configuration are populated with "
                    "classes, not instances."
                )
            if not issubclass(form_class, ModelForm):
                raise InvalidSupergoodReadsConfigError(
                    f"{form_class} is not a ModelForm."
                )
            if not issubclass(form_class._meta.model, AbstractStrategy):
                raise InvalidSupergoodReadsConfigError(
                    f"The Model for {form_class} is not a subclass of AbstractStrategy."
                )

    def _validate_media_type_form_classes(self) -> None:
        """Validate that media_type_form_classes are MediaTypes."""
        for form_class in self.media_type_form_classes:
            if not isinstance(form_class, type):
                raise InvalidSupergoodReadsConfigError(
                    "Expected an uninstantiated form class, but got an instance: "
                    f"{form_class}. Please ensure strategy_form_classes and "
                    "media_type_form_classes in your configuration are populated with "
                    "classes, not instances."
                )
            if not issubclass(form_class, ModelForm):
                raise InvalidSupergoodReadsConfigError(
                    f"{form_class} is not a ModelForm."
                )
            if not issubclass(form_class._meta.model, AbstractMediaType):
                raise InvalidSupergoodReadsConfigError(
                    f"The Model for {form_class} is not a subclass of AbstractMediaType."
                )

    @final
    @property
    def strategy_model_classes(self) -> list[Type[Model]]:
        return [
            form._meta.model
            for form in supergood_reads_engine.config.strategy_form_classes
        ]

    @final
    @property
    def media_type_model_classes(self) -> list[Type[Model]]:
        return [
            form._meta.model
            for form in supergood_reads_engine.config.media_type_form_classes
        ]

    def demo_review_queryset(self) -> QuerySet[Review]:
        """
        The QuerySet that generates the Reviews that non logged-in users will see on the
        my_reviews page, for demo purposes only. Defaults to empty.

        Users can override this method in a subclass to return a custom QuerySet.
        """
        return Review.objects.none()

    def demo_media_queryset(self) -> QuerySet[Any]:
        """
        The QuerySet that generates the Media objects that non logged-in users will see
        on the my_media page, for demo purposes only. Defaults to empty.

        Users can override this method in a subclass to return a custom QuerySet.
        """
        return Book.objects.none()


class DefaultSupergoodReadsConfig(SupergoodReadsConfig):
    strategy_form_classes = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_form_classes = [
        BookAutocompleteForm,
        FilmAutocompleteForm,
    ]


class SupergoodReadsEngine:
    """
    The SupergoodReadsEngine class uses the configuration defined in SupergoodReadsConfig or its subclasses to
    handle operations related to the Supergood Reads application.
    """

    def __init__(self, config_cls: Optional[Type[SupergoodReadsConfig]] = None):
        self._config_cls = config_cls
        self.config = self.get_config()

    def get_config(self) -> SupergoodReadsConfig:
        """
        If a SupergoodReadsConfig subclass was passed to the constructor, it is used.
        Otherwise, it tries to fetch a configuration class from
        SUPERGOOD_READS_CONFIG in Django settings.
        If neither are provided, DefaultSupergoodReadsConfig is used.
        """
        config_str = getattr(settings, SUPERGOOD_READS_CONFIG, None)
        if self._config_cls:
            config_cls = self._config_cls
        elif config_str:
            try:
                config_cls = import_string(config_str)
            except ImportError as e:
                raise InvalidSupergoodReadsConfigError(
                    f"Could not find SupergoodReadsConfig '{config_str}': {e}"
                )
        else:
            config_cls = DefaultSupergoodReadsConfig

        # Make sure the config is a subclass of BaseSupergoodReadsConfig
        if not issubclass(config_cls, SupergoodReadsConfig):
            raise InvalidSupergoodReadsConfigError(
                f"{config_cls} is not a subclass of SupergoodReadsConfig."
            )

        return config_cls()


supergood_reads_engine = SupergoodReadsEngine()
