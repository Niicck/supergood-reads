import json
from typing import no_type_check

from django import template
from django.utils.html import (  # type: ignore [attr-defined]
    _json_script_escapes,
    format_html,
)
from django.utils.safestring import SafeText, mark_safe

register = template.Library()


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


@register.filter()
def to_js_bool(value: bool) -> str:
    """
    Convert a python Boolean into a boolean value that can be parsed by vue javascript.
    Use this when passing evaluated booleans as props to vue components.

    Example:
        <custom-component :enabled={{ enabled|to_js_bool }}><custom-component>
    """
    if value is True:
        return "true"
    else:
        return "false"
