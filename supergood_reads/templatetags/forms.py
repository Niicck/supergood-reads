from typing import Any, Dict

from django import template
from django.forms import BoundField
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def supergood_field(
    field: BoundField,
    border: bool = True,
    label_above: bool = False,
) -> str:
    """Renders a form field. Returns context variables to support.

    Returns:
      field:
        The form field to render.
      field_type:
        The default widget type for the field.
      border:
        Draw a border around the field, or don't.
      label_above:
    """
    context = {
        "field": field,
        "border": border,
        "label_above": label_above,
    }

    field_type = field.widget_type
    field_template_options = ["number", "radioselect", "textarea"]
    if field_type in field_template_options:
        template_name = f"supergood_reads/components/forms/fields/{field_type}.html"
    else:
        template_name = "supergood_reads/components/forms/fields/default.html"

    return render_to_string(template_name, context)


@register.inclusion_tag(
    "supergood_reads/components/forms/custom_fields/date_picker.html"
)
def date_picker(
    day_field: BoundField,
    month_field: BoundField,
    year_field: BoundField,
    label_above: bool = True,
) -> Dict[str, Any]:
    return {
        "day_field": day_field,
        "month_field": month_field,
        "year_field": year_field,
        "label_above": label_above,
    }


@register.inclusion_tag("supergood_reads/components/forms/layout/_subheading.html")
def form_subheading(title: str, text: str) -> dict[str, Any]:
    return {
        "title": title,
        "text": text,
    }
