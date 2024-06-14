from django.http import HttpRequest

from app.settings.base import APP_NAME
from main.models import Announcement
from posts.models import PostType
from datetime import datetime
from user_agents import parse


def base_processors(request: HttpRequest):
    advertisements = Announcement.objects.filter(is_active=True)
    post_types = PostType.objects.all()
    current_year = datetime.now().year
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    return {'site_main_title': APP_NAME,
            'advertisements': advertisements,
            'current_year': current_year,
            'post_types': post_types,
            'user_agent': user_agent,
            }
