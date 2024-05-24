from django.utils.http import urlencode
from django.utils import translation
from django import template

from bs4 import BeautifulSoup
import humanize
import bleach
import os

register = template.Library()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.filter
def clear_tags(value):
    text = BeautifulSoup(value, 'html.parser')
    return text.get_text()


@register.filter
def bleach_linkify(value):
    return bleach.clean(value)


@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def humanize_naturaltime(value):
    humanize.i18n.activate(translation.get_language())
    time = humanize.naturaltime(value)
    return time


@register.filter
def bleach_xss(value):
    ALLOWED_TAGS = frozenset(
        (
            "i",
            "a",
            "p",
            "b",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "img",
            'em',
            "pre",
            "code",
            "abbr",
            "acronym",
            "blockquote",
            "em",
            "li",
            "ol",
            "strong",
            "ul",
            "span",
            "mark",
            "sub",
            "sup",
            "figure",
        ))
    ALLOWED_ATTRIBUTES = {
        "img": ['href', 'title', 'src', 'srcset', 'alt', 'style', 'data-wpel-link',
                'sizes', 'width', 'height'],
        "a": ["href", "title", 'data-wpel-link'],
        "p": ["style"],
        "h1": ["style"],
        "h2": ["style"],
        "h3": ["style"],
        "abbr": ["title"],
        "acronym": ["title"],
        "span": ["style"],
        "figure": ["image", "style"],
    }

    return bleach.clean(value, ALLOWED_TAGS)

@register.filter
def bleach_comments(value):
    ALLOWED_TAGS = frozenset(
        (
            'a',
            'i',
            'p',
            'u',
            's',
            'sub',
            'sup',
            'pre',
            'code',
            'blockquote',
            'strong',
            'span',
            'mark',
            'figure',
            'img'
        ))
    ALLOWED_ATTRIBUTES = {
        "a": ["href", "title", 'data-wpel-link'],
        "figure": ["image"],
        "img": ['href', 'title', 'src', 'srcset', 'alt', 'data-wpel-link',
                'sizes', 'width', 'height'],
    }

    return bleach.clean(value, ALLOWED_TAGS, ALLOWED_ATTRIBUTES)
