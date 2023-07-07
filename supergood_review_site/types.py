from typing import TypeVar

from supergood_review_site.models import AbstractMediaType, AbstractStrategy

# Type that allows a instance of any subclass of AbstractMediaType
TMedia = TypeVar("TMedia", bound=AbstractMediaType)

# Type that allows a instance of any subclass of AbstractStrategy
TStrategy = TypeVar("TStrategy", bound=AbstractStrategy)
