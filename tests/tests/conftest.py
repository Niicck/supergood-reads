from typing import Any

import pytest

from supergood_reads.media_types.forms import BookForm, FilmForm
from supergood_reads.strategies.forms import (
    EbertStrategyForm,
    GoodreadsStrategyForm,
    MaximusStrategyForm,
)
from supergood_reads.utils.engine import SupergoodReadsConfig


class PytestSupergoodReadsConfig(SupergoodReadsConfig):
    strategy_form_classes = [
        EbertStrategyForm,
        GoodreadsStrategyForm,
        MaximusStrategyForm,
    ]
    media_type_form_classes = [
        BookForm,
        FilmForm,
    ]


@pytest.fixture(autouse=True)
def use_pytest_settings(settings: Any) -> None:
    # Only use a subset of strategies and media_types while testing.
    settings.SUPERGOOD_READS_CONFIG = "tests.tests.conftest.PytestSupergoodReadsConfig"
