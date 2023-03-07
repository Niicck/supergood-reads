from typing import Any, cast

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


class Utils:
    @classmethod
    def get_content_type_id(cls, model: Any) -> int:
        """Get the content_type id for a model.

        Due to covariance issues, mypy doesn't recognize specific Model subclasses as
        Models. To work around this, we explicitly cast our model as a Model.
        """
        cast(Model, model)
        return ContentType.objects.get_for_model(model).id
