from enum import Enum
from typing import Any, Dict, Literal, Optional, Union

from django import template
from django.forms.boundfield import BoundField

register = template.Library()


class CustomFieldType(Enum):
    ALGOLIA_AUTOCOMPLETE = "algolia_autocomplete"


CustomFieldTypeOption = Literal[CustomFieldType.ALGOLIA_AUTOCOMPLETE,]


@register.inclusion_tag("common/field_wrapper.html")
def field_wrapper(
    field: BoundField,
    border: bool = True,
    field_type: Optional[CustomFieldTypeOption] = None,
) -> Dict[str, Any]:
    """Renders a form field.
    Args:
      field:
        The form field to render.
      border:
        Indicate whether to draw a border around field.
      field_type:
        Override default Field Widget rendering instructions.
    """
    rendered_field_type: Union[CustomFieldTypeOption, str] = (
        field_type or field.widget_type
    )
    return {
        "field": field,
        "field_type": rendered_field_type,
        "border": border,
    }
