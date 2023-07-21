from typing import Any, TypedDict

from django import template
from django.forms import ModelForm
from django.template import Context
from django.urls import reverse

from supergood_review_site.media_types.forms import MyMediaBookForm, MyMediaFilmForm
from supergood_review_site.media_types.models import AbstractMediaType, Book, Film

register = template.Library()


@register.inclusion_tag("supergood_review_site/_nav_bar.html", takes_context=True)
def nav_bar(context: Context) -> Context:
    """
    Returns:
      nav_bar_links:
        a list of links to render in the Nav Bar. These are written to a json_script
        within the django template and then parsed by vue.js template.
    """
    current_url = context["request"].get_full_path()
    return Context(
        {
            "nav_bar_links": [
                {
                    "name": "Create Review",
                    "href": reverse("create_review"),
                    "current": reverse("create_review") == current_url,
                },
                {
                    "name": "My Media",
                    "href": reverse("media"),
                    "current": reverse("media") == current_url,
                },
                {
                    "name": "My Reviews",
                    "href": reverse("reviews"),
                    "current": reverse("reviews") == current_url,
                },
            ]
        }
    )


class MyMediaRowContext(TypedDict, total=False):
    item: AbstractMediaType
    form: ModelForm[Any]


@register.inclusion_tag("supergood_review_site/_media_row.html")
def media_row(item: AbstractMediaType) -> MyMediaRowContext:
    """
    Renders a row on the "My Media" page.
    """
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
        item=item,
        form=form_class(),
    )
