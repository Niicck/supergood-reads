import pytest
from django.contrib.contenttypes.models import ContentType

from supergood_reads.models import Book
from supergood_reads.utils import ContentTypeUtils


@pytest.mark.django_db
def test_get_content_type_id() -> None:
    book_content_type_id = ContentTypeUtils.get_content_type_id(Book)
    assert ContentType.objects.get_for_id(book_content_type_id).model_class() == Book
