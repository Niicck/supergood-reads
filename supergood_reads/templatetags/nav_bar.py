from typing import TypedDict

from django import template
from django.template import Context
from django.urls import reverse

register = template.Library()


class NavBarLink(TypedDict):
    label: str
    url: str
    current: bool


def nav_bar_links_factory(
    data: list[tuple[str, str]], current_url: str
) -> list[NavBarLink]:
    return [
        NavBarLink(label=label, url=url, current=current_url == url)
        for label, url in data
    ]


@register.inclusion_tag("supergood_reads/_nav_bar.html", takes_context=True)
def nav_bar(context: Context) -> Context:
    current_url = context["request"].get_full_path()

    primary_links_data = [
        ("Reviews", reverse("reviews")),
        ("Media", reverse("media")),
    ]

    account_links_data = [("Settings", "#"), ("Sign out", reverse("logout"))]

    primary_nav_bar_links = nav_bar_links_factory(primary_links_data, current_url)
    account_nav_bar_links = nav_bar_links_factory(account_links_data, current_url)

    context.update(
        {
            "primary_nav_bar_links": primary_nav_bar_links,
            "account_nav_bar_links": account_nav_bar_links,
        }
    )

    return context
