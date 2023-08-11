import json
from typing import Any, Dict, no_type_check

from django import template
from django.forms import Form
from django.forms.boundfield import BoundField
from django.forms.fields import ChoiceField
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import (  # type: ignore [attr-defined]
    _json_script_escapes,
    format_html,
)
from django.utils.safestring import SafeText, mark_safe

from supergood_reads.utils import forms as form_utils

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


@no_type_check
@register.filter(is_safe=True)
def vue_json_script(value, element_id=None, encoder=None) -> SafeText:
    """
    A modified "json_script" filter that works within vue applications.
    Replaces "json_script" filter's template with vue_json_script_template.

    If you try to use the json_script filter within a vue application (i.e. within a
    child html element of the root component that the vue app is mounted onto), then the
    outputted <script> will not be read. You will instead see this error:

    [Vue warn]: Template compilation error: Tags with side effect (<script> and <style>)
    are ignored in client component templates.

    In order to be compatible with vue, the output of our json_script must be wrapped in
    the vue_json_script_template.

    Attributes of vue_json_script_template:
    v-pre:
        Disables vue compilation. This will prevent valid json code from conflicting
        with vue delimiters.
    v-show=false:
        Hides the json that would be rendered since compilation was diabled with v-pre.
    :is="\'script\'"
        Indicates that this component should be treated like a <script/>.
    """
    from django.core.serializers.json import DjangoJSONEncoder

    vue_json_script_template = '<div v-show="false"><component v-pre :is="\'script\'" id="{}" type="application/json">{}</component></div>'

    json_str = json.dumps(value, cls=encoder or DjangoJSONEncoder).translate(
        _json_script_escapes
    )
    if element_id:
        # The following line is the only difference from django.utils.html.json_script
        template = vue_json_script_template
        args = (element_id, mark_safe(json_str))  # noqa: S703,S308
    else:
        template = '<script type="application/json">{}</script>'
        args = (mark_safe(json_str),)  # noqa: S703,S308
    return format_html(template, *args)


@register.filter(is_safe=True)
def get_initial_field_value(form: Form, field_name: str) -> Any:
    return form_utils.get_initial_field_value(form, field_name)


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
        template_name = f"supergood_reads/forms/fields/{field_type}.html"
    else:
        template_name = "supergood_reads/forms/fields/default.html"

    return render_to_string(template_name, context)


@register.inclusion_tag(
    "supergood_reads/forms/custom_fields/autocomplete.html", takes_context=True
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


def date_picker_field():
    pass


@register.inclusion_tag("supergood_reads/forms/custom_fields/radio_cards.html")
def radio_cards_field(field: BoundField, state_key: str) -> dict[str, Any]:
    field_data_json_script_id = f"radio_cards_json_script_id_{field.id_for_label}"

    context = {
        "field": field,
        "state_key": state_key,
        "field_data_json_script_id": field_data_json_script_id,
    }

    return context
