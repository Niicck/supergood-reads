from typing import Any, Optional, Type

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelForm
from django.utils.module_loading import import_string

from supergood_reads.forms.media_item_forms import BookForm, FilmForm
from supergood_reads.forms.strategy_forms import (
    EbertStrategyForm,
    GoodreadsStrategyForm,
    ImdbStrategyForm,
    LetterboxdStrategyForm,
    ThumbsStrategyForm,
    TomatoStrategyForm,
)
from supergood_reads.models import AbstractReviewStrategy, BaseMediaItem

SUPERGOOD_READS_CONFIG = "SUPERGOOD_READS_CONFIG"


class InvalidSupergoodReadsConfigError(ImproperlyConfigured):
    pass


class SupergoodReadsConfig:
    """
    Base configuration class for a supergood_reads application.
    You can subclass this to provide custom configurations for your own application.
    """

    """
    Strategies that are eligible to be selected when creating a new Review.
    Users can override this variable in a subclass to return their own strategies.
    """
    strategy_form_classes: list[Type[ModelForm[Any]]] = []

    """
    MediaItems are eligible to be selected when creating a new Review.
    Users can override this variable in a subclass to return their own media_items.
    """
    media_item_form_classes: list[Type[ModelForm[Any]]] = []


class DefaultSupergoodReadsConfig(SupergoodReadsConfig):
    strategy_form_classes = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        ImdbStrategyForm,
        ThumbsStrategyForm,
        LetterboxdStrategyForm,
        TomatoStrategyForm,
    ]
    media_item_form_classes = [
        BookForm,
        FilmForm,
    ]


class SupergoodReadsEngine:
    """
    The SupergoodReadsEngine class uses the configuration defined in SupergoodReadsConfig or its subclasses to
    handle operations related to the Supergood Reads application.
    """

    def __init__(self, config_cls: Optional[Type[SupergoodReadsConfig]] = None):
        self._config_cls = config_cls
        self.config = self.get_config()
        self.strategy_form_classes = self.config.strategy_form_classes
        self.media_item_form_classes = self.config.media_item_form_classes
        self.validate_strategy_form_classes()
        self.validate_media_item_form_classes()
        self.strategy_model_classes: list[type[AbstractReviewStrategy]] = [
            form._meta.model for form in self.strategy_form_classes
        ]
        self.media_item_model_classes: list[type[BaseMediaItem]] = [
            form._meta.model for form in self.media_item_form_classes
        ]

    def get_config(self) -> SupergoodReadsConfig:
        """
        If a SupergoodReadsConfig subclass was passed to the constructor, it is used.
        Otherwise, it tries to fetch a configuration class from SUPERGOOD_READS_CONFIG
        in Django settings.
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

    def validate_strategy_form_classes(self) -> None:
        """Validate that all strategy_form_classes are Strategies."""
        for form_class in self.strategy_form_classes:
            if not isinstance(form_class, type):
                raise InvalidSupergoodReadsConfigError(
                    "Expected an uninstantiated form class, but got an instance: "
                    f"{form_class}. Please ensure strategy_form_classes and "
                    "media_item_form_classes in your configuration are populated with "
                    "classes, not instances."
                )
            if not issubclass(form_class, ModelForm):
                raise InvalidSupergoodReadsConfigError(
                    f"{form_class} is not a ModelForm."
                )
            if not issubclass(form_class._meta.model, AbstractReviewStrategy):
                raise InvalidSupergoodReadsConfigError(
                    f"The Model for {form_class} is not a subclass of AbstractReviewStrategy."
                )

    def validate_media_item_form_classes(self) -> None:
        """Validate that media_item_form_classes are MediaItems."""
        for form_class in self.media_item_form_classes:
            if not isinstance(form_class, type):
                raise InvalidSupergoodReadsConfigError(
                    "Expected an uninstantiated form class, but got an instance: "
                    f"{form_class}. Please ensure strategy_form_classes and "
                    "media_item_form_classes in your configuration are populated with "
                    "classes, not instances."
                )
            if not issubclass(form_class, ModelForm):
                raise InvalidSupergoodReadsConfigError(
                    f"{form_class} is not a ModelForm."
                )
            if not issubclass(form_class._meta.model, BaseMediaItem):
                raise InvalidSupergoodReadsConfigError(
                    f"The Model for {form_class} is not a subclass of BaseMediaItem."
                )


supergood_reads_engine = SupergoodReadsEngine()
