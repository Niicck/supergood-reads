from typing import Any, Dict

from django import template
from django.forms.boundfield import BoundField

register = template.Library()


@register.inclusion_tag("common/field_wrapper.html")
def field_wrapper(field: BoundField, border: bool = True) -> Dict[str, Any]:
    """Renders a form field.
    Args:
      field: the form field to render.
      border: indicate whether to draw a border around your field or not.
    """
    field_type = field.widget_type
    return {
        "field": field,
        "field_type": field_type,
        "border": border,
    }
