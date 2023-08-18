from typing import Any, Dict

from django import template
from django.forms import Form
from django.forms.boundfield import BoundField
from django.forms.fields import ChoiceField
from django.template import Context
from django.template.loader import render_to_string

from supergood_reads.utils.forms import (
    get_initial_field_value as get_initial_field_value_util,
)

register = template.Library()


@register.filter(is_safe=True)
def field_to_dict(field: BoundField) -> Dict[str, Any]:
    """Convert django field into dict consumable by vue Component props."""
    if isinstance(field.field, ChoiceField):
        choices = field.field.choices
    else:
        choices = []
    field_data = {
        "html_name": field.html_name,
        "label": field.label,
        "id_for_label": field.id_for_label,
        "choices": choices,
    }
    return field_data


@register.filter(is_safe=True)
def get_initial_field_value(form: Form, field_name: str) -> Any:
    return get_initial_field_value_util(form, field_name)


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
    "supergood_reads/components/forms/custom_fields/autocomplete.html",
    takes_context=True,
)
def autocomplete_field(
    context: Context,
    field: BoundField,
    state_key: str,
    url: str,
    initial_value_id: str,
) -> Context:
    field_data_json_script_id = f"autocomplete_json_script_id_{field.id_for_label}"

    context.update(
        {
            "field": field,
            "state_key": state_key,
            "field_data_json_script_id": field_data_json_script_id,
            "url": url,
            "initial_value_id": initial_value_id,
        }
    )

    return context


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


@register.inclusion_tag(
    "supergood_reads/components/forms/custom_fields/radio_cards.html"
)
def radio_cards_field(field: BoundField, state_key: str) -> dict[str, Any]:
    field_data_json_script_id = f"radio_cards_json_script_id_{field.id_for_label}"

    context = {
        "field": field,
        "state_key": state_key,
        "field_data_json_script_id": field_data_json_script_id,
    }

    return context


@register.inclusion_tag("supergood_reads/components/forms/layout/_subheading.html")
def form_subheading(title: str, text: str) -> dict[str, Any]:
    return {
        "title": title,
        "text": text,
    }
