import pytest
from django.contrib.contenttypes.models import ContentType

from django_flex_reviews.media_types.models import Book
from django_flex_reviews.utils import Utils


@pytest.mark.django_db
def test_get_content_type_id() -> None:
    book_content_type_id = Utils.get_content_type_id(Book)
    assert ContentType.objects.get_for_id(book_content_type_id).model_class() == Book
