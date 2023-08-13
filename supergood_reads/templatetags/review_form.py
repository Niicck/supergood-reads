from django import template
from django.template import Context

register = template.Library()


@register.inclusion_tag(
    "supergood_reads/views/review_form/_select_media_type.html", takes_context=True
)
def select_media_type(context: Context) -> Context:
    return context


@register.inclusion_tag(
    "supergood_reads/views/review_form/_select_strategy.html", takes_context=True
)
def select_strategy(context: Context) -> Context:
    return context


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
