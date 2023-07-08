from typing import Any, Optional, TypedDict
from uuid import UUID

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
                    "href": reverse("my_media"),
                    "current": reverse("my_media") == current_url,
                },
                {"name": "My Reviews", "href": "#", "current": False},
            ]
        }
    )


class MyMediaRowContext(TypedDict, total=False):
    item: AbstractMediaType
    id: UUID
    title: str
    author: str
    year: Optional[int]
    media_type: str
    form: ModelForm[Any]


@register.inclusion_tag("supergood_review_site/_my_media_row.html")
def media_row(item: AbstractMediaType) -> MyMediaRowContext:
    """
    Renders a row on the "My Media" page.
    """
    if isinstance(item, Book):
        return MyMediaRowContext(
            item=item,
            id=item.id,
            title=item.title,
            author=item.author,
            year=item.publication_year,
            media_type=str(Book._meta.verbose_name),
            form=MyMediaBookForm(instance=item),
        )
    elif isinstance(item, Film):
        return MyMediaRowContext(
            item=item,
            id=item.id,
            title=item.title,
            author=item.director,
            year=item.release_year,
            media_type=str(Film._meta.verbose_name),
            form=MyMediaFilmForm(instance=item),
        )
    else:
        raise NotImplementedError(
            f"{type(item)} is not supported by media_row inclusion_tag"
        )
