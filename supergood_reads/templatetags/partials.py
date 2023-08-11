from typing import Any, TypedDict

from django import template
from django.forms import ModelForm

from supergood_reads.media_types.forms import MyMediaBookForm, MyMediaFilmForm
from supergood_reads.media_types.models import AbstractMediaType, Book, Film

register = template.Library()


class MyMediaRowContext(TypedDict, total=False):
    item: AbstractMediaType
    form: ModelForm[Any]
    enabled: bool


@register.inclusion_tag("supergood_reads/_media_row.html", takes_context=True)
def media_row(context: Any, item: AbstractMediaType) -> MyMediaRowContext:
    """
    Renders a row on the "My Media" page.
    """
    request = context.get("request")

    form_class: type[ModelForm[Any]]
    if isinstance(item, Book):
        form_class = MyMediaBookForm
    elif isinstance(item, Film):
        form_class = MyMediaFilmForm
    else:
        raise NotImplementedError(
            f"{type(item)} is not supported by media_row inclusion_tag"
        )

    return MyMediaRowContext(
        item=item, form=form_class(), enabled=item.can_user_change(request.user)
    )
