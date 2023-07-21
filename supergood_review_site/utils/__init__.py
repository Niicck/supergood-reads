from typing import Any, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


class ContentTypeUtils:
    @classmethod
    def get_content_type_id(cls, model: Any) -> int:
        """Get the content_type id for a model."""
        return ContentType.objects.get_for_model(model).id

    @classmethod
    def get_model(cls, content_type_id: int) -> Type[Model]:
        model = ContentType.objects.get_for_id(content_type_id).model_class()
        assert model
        return model
