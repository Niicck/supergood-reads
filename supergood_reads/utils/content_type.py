from typing import Any, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


def model_to_content_type_id(model: Any) -> int:
    """Get the content_type id for a model."""
    return ContentType.objects.get_for_model(model).id


def content_type_id_to_model(content_type_id: int) -> Type[Model]:
    """Get the model from content_type_id."""
    model = ContentType.objects.get_for_id(content_type_id).model_class()
    if not model:
        raise LookupError
    return model
