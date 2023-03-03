from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


class Utils:
    @classmethod
    def get_content_type_id(cls, model: Model) -> int:
        return ContentType.objects.get_for_model(model).id
