from typing import Any

from django import template
from django.forms import Form

from supergood_reads.media_types.models import AbstractMediaType, Book, Film
from supergood_reads.utils import forms as form_utils

register = template.Library()


@register.filter()
def get_media_type_form_ref(media_type_id: int) -> str:
    """Generate ref= attribute for media_type_form with specific media_type_id.

    This will allow the vue toggleRequiredFieldsOnForms watcher to target the specific
    form that corresponds to this media_type_id.
    """
    return f"media_type_form_{media_type_id}"


@register.filter()
def get_strategy_form_ref(strategy_id: int) -> str:
    """Generate ref= attribute for strategy_form with specific media_type_id.

    This will allow the vue toggleRequiredFieldsOnForms watcher to target the specific
    form that corresponds to this strategy_id.
    """
    return f"strategy_form_{strategy_id}"


@register.filter(is_safe=True)
def get_initial_field_value(form: Form, field_name: str) -> Any:
    return form_utils.get_initial_field_value(form, field_name)


@register.filter()
def is_book(item: AbstractMediaType) -> bool:
    return isinstance(item, Book)


@register.filter()
def is_film(item: AbstractMediaType) -> bool:
    return isinstance(item, Film)


@register.filter()
def int_to_str(value: int | None) -> str | None:
    if value is None:
        return None
    else:
        return str(value)
