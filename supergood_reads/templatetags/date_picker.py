from typing import Any, Dict

from django import template
from django.forms.boundfield import BoundField

register = template.Library()


@register.inclusion_tag("supergood_reads/forms/_date_picker.html")
def date_picker(
    day_field: BoundField,
    month_field: BoundField,
    year_field: BoundField,
    border: bool = True,
    label_above: bool = True,
) -> Dict[str, Any]:
    return {
        "day_field": day_field,
        "month_field": month_field,
        "year_field": year_field,
        "border": border,
        "label_above": label_above,
    }
