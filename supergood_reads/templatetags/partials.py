from typing import Any, cast

from django import template
from django.forms import ModelForm
from django.http import HttpRequest
from django.template import Context

from supergood_reads.media_types.forms import MyMediaBookForm, MyMediaFilmForm
from supergood_reads.media_types.models import AbstractMediaType, Book, Film

register = template.Library()


@register.inclusion_tag("supergood_reads/_media_row.html", takes_context=True)
def media_row(context: Context, item: AbstractMediaType) -> Context:
    """
    Renders a row on the "My Media" page.
    """
    request = cast(HttpRequest, context.get("request"))

    form_class: type[ModelForm[Any]]
    if isinstance(item, Book):
        form_class = MyMediaBookForm
    elif isinstance(item, Film):
        form_class = MyMediaFilmForm
    else:
        raise NotImplementedError(
            f"{type(item)} is not supported by media_row inclusion_tag"
        )

    context.update(
        {
            "item": item,
            "form": form_class(),
            "enabled": item.can_user_change(request.user),
        }
    )

    return context
