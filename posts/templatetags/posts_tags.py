from django.utils.http import urlencode
from django import template

from posts.models import PostType

register = template.Library()


@register.filter()
def all_post_types():
    return PostType.objects.all()


@register.filter()
def rating_to_text(value):
    if value >= 90:
        return 'ЧУДОВО'
    elif value >= 80:
        return 'ВІДМІННО'
    elif value >= 70:
        return 'ВАРТЕ УВАГИ'
    elif value >= 60:
        return 'ЗАДОВІЛЬНО'
    elif value >= 50:
        return 'СЕРЕДНЯК'
    elif value >= 40:
        return 'НЕ ДУЖЕ'
    elif value >= 30:
        return 'ПОГАНЕНЬКО'
    elif value >= 20:
        return 'ПОГАНО'
    else:
        return 'ЖАХЛИВО'


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
