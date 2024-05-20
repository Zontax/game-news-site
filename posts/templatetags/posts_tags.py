from django.utils.http import urlencode
from django import template
from posts.models import PostType

register = template.Library()

@register.simple_tag()
def all_post_types():
    return PostType.objects.all()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
