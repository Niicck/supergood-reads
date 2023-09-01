import pytest
from django.forms import ModelForm

from supergood_reads.models import (
    AbstractReviewStrategy,
    BaseMediaItem,
    Book,
    EbertStrategy,
)
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
        class NewStrategy(AbstractReviewStrategy):
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

    def test_valid_new_media_item(self) -> None:
        class NewMedia(BaseMediaItem):
            class Meta:
                app_label = "test"

        class NewMediaForm(ModelForm[NewMedia]):
            class Meta:
                model = NewMedia
                fields = "__all__"

        class GoodConfig(SupergoodReadsConfig):
            media_item_form_classes = [NewMediaForm]

        assert SupergoodReadsEngine(config_cls=GoodConfig)

    def test_invalid_media_item(self) -> None:
        class BadClass:
            pass

        class BadConfig(SupergoodReadsConfig):
            media_item_form_classes = [BadClass]  # type: ignore[list-item]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)

    def test_invalid_media_item_form(self) -> None:
        class BadClass(ModelForm[EbertStrategy]):
            class Meta:
                model = EbertStrategy
                fields = "__all__"

        class BadConfig(SupergoodReadsConfig):
            media_item_form_classes = [BadClass]

        with pytest.raises(InvalidSupergoodReadsConfigError):
            SupergoodReadsEngine(config_cls=BadConfig)
