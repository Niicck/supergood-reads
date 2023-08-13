from django import template

register = template.Library()


@register.inclusion_tag("supergood_reads/components/_basic_header.html")
def basic_header(title: str) -> dict[str, str]:
    return {"title": title}
