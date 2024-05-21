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


@register.filter()
def rating_to_color(value):
    if value >= 90:
        return 'rgb(61, 205, 9)'
    elif value >= 80:
        return 'rgb(61, 205, 9)'
    elif value >= 70:
        return 'rgb(61, 205, 9)'
    elif value >= 60:
        return 'orange'
    elif value >= 50:
        return 'darkorange'
    elif value >= 40:
        return 'orangered'
    else:
        return 'red'
