import json
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union, no_type_check

from django import template
from django.forms.boundfield import BoundField
from django.forms.fields import ChoiceField
from django.utils.html import (  # type: ignore [attr-defined]
    _json_script_escapes,
    format_html,
)
from django.utils.safestring import SafeText, mark_safe

register = template.Library()


class CustomFieldType(Enum):
    ALGOLIA_AUTOCOMPLETE = "algolia_autocomplete"
    RADIO_CARDS = "radio_cards"


CustomFieldTypeOption = Literal[
    CustomFieldType.ALGOLIA_AUTOCOMPLETE, CustomFieldType.RADIO_CARDS
]


@register.inclusion_tag("django_flex_reviews/_field_wrapper.html")
def field_wrapper(
    field: BoundField,
    border: bool = True,
    label_above: bool = False,
    field_type: Optional[CustomFieldTypeOption] = None,
    state_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Renders a form field. Returns context variables to support.

    Returns:
      field:
        The form field to render.
      border:
        Indicate whether to draw a border around field.
      field_type:
        Defaults to the field's widget_type. However, the inclusion template
        supports custom field rendering for the types listed in CustomFieldType.
      radio_cards_json_script_id:
        If field_type == "radio_type", then also return radio_cards_json_script_id which
        identifies the html element where the jsonified field data will be stored.
      state_key:
        Some form inputs need to be bound to a state in our vue pinia store.

        Usually, this can be accomplished by adding the attribute
        "v-model:store.[[state_key]]" to the field html element directly.

        But some form input renderings are more complicated. They might need to be
        rendered by a custom vue component within this field_wrapper template.

        You can't pass a v-model to a child vue component and have it dynamically update
        the parent vue component.

        But the child vue component can directly update the pinia store without talking
        to its parent.

        By passing in the state_key as a string directly to the child, we can create an
        abstract way to bind any vue component to any attribute in our state, without
        hardcoding anything.
    """
    rendered_field_type: Union[CustomFieldTypeOption, str] = (
        field_type or field.widget_type
    )

    if rendered_field_type == "radio_cards":
        radio_cards_json_script_id: Optional[
            str
        ] = f"radio_cards_json_script_id_{field.id_for_label}"
    else:
        radio_cards_json_script_id = None

    return {
        "field": field,
        "field_type": rendered_field_type,
        "border": border,
        "label_above": label_above,
        "radio_cards_json_script_id": radio_cards_json_script_id,
        "state_key": state_key,
    }


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


"""
Attributes:
  v-pre:
    Disables vue compilation. This will prevent valid json code from conflicting with vue delimiters.
  v-show=false:
    Hides the json that would be rendered since compilation was diabled with v-pre.
  :is="\'script\'"
    Indicates that this component should be treated like a <script/>. Yes, the escaped
    single quotes are mandatory.
"""
vue_json_script_template = '<div v-show="false"><component v-pre :is="\'script\'" id="{}" type="application/json">{}</component></div>'


@no_type_check
@register.filter(is_safe=True)
def vue_json_script(value, element_id=None, encoder=None) -> SafeText:
    """
    Modify default json_script filter to work with vue.

    If you try to use the json_script filter within a vue application (i.e. within a
    child html element of the root component that the vue app is mounted onto), then the
    outputted <script> will not be read. You will instead see this error:

    [Vue warn]: Template compilation error: Tags with side effect (<script> and <style>)
    are ignored in client component templates.

    In order to be compatible with vue, the output of our json_script must be wrapped in
    the vue_json_script_template.
    """
    from django.core.serializers.json import DjangoJSONEncoder

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
def get_media_type_form_ref(media_type_id: int) -> str:
    return f"media_type_form_{media_type_id}"


@register.filter(is_safe=True)
def get_strategy_form_ref(strategy_id: int) -> str:
    return f"strategy_form_{strategy_id}"
