import pytest
from django.forms import ModelForm

from supergood_reads.media_types.models import AbstractMediaType
from supergood_reads.models import Book, EbertStrategy
from supergood_reads.strategies.models import AbstractStrategy
from supergood_reads.utils.engine import (
    InvalidSupergoodReadsConfigError,
    SupergoodReadsConfig,
    SupergoodReadsEngine,
)


class TestSupergoodReadsEngine:
    def test_invalid_config(self) -> None:
        class BadConfig:
            pass

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)  # type: ignore[arg-type]

    def test_valid_new_strategy(self) -> None:
        class NewStrategy(AbstractStrategy):
            class Meta:
                app_label = "test"

        class NewStrategyForm(ModelForm[NewStrategy]):
            class Meta:
                model = NewStrategy
                fields = "__all__"

        class GoodConfig(SupergoodReadsConfig):
            strategy_form_classes = [NewStrategyForm]

        assert SupergoodReadsEngine(config_cls=GoodConfig)

    def test_invalid_strategy(self) -> None:
        class BadClass:
            pass

        class BadConfig(SupergoodReadsConfig):
            strategy_form_classes = [BadClass]  # type: ignore[list-item]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)

    def test_invalid_strategy_form(self) -> None:
        class BadClass(ModelForm[Book]):
            class Meta:
                model = Book
                fields = "__all__"

        class BadConfig(SupergoodReadsConfig):
            strategy_form_classes = [BadClass]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)

    def test_valid_new_media_type(self) -> None:
        class NewMedia(AbstractMediaType):
            class Meta:
                app_label = "test"

        class NewMediaForm(ModelForm[NewMedia]):
            class Meta:
                model = NewMedia
                fields = "__all__"

        class GoodConfig(SupergoodReadsConfig):
            media_type_form_classes = [NewMediaForm]

        assert SupergoodReadsEngine(config_cls=GoodConfig)

    def test_invalid_media_type(self) -> None:
        class BadClass:
            pass

        class BadConfig(SupergoodReadsConfig):
            media_type_form_classes = [BadClass]  # type: ignore[list-item]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)

    def test_invalid_media_type_form(self) -> None:
        class BadClass(ModelForm[EbertStrategy]):
            class Meta:
                model = EbertStrategy
                fields = "__all__"

        class BadConfig(SupergoodReadsConfig):
            media_type_form_classes = [BadClass]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)
