from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from app.settings.base import APP_NAME
from posts.models import Post


class LatestPostsFeed(Feed):
    title = APP_NAME
    description_template = 'posts/feed_description.html'
    link = reverse_lazy('posts:feed')
    description = f'Нові публікації на сайті {APP_NAME}'
    language = 'uk'

    def items(self):
        return Post.published.all()[:10]

    def item_title(self, item: Post):
        return item.title

    def item_description(self, item: Post):
        return truncatewords_html(item.content, 30)

    def item_pubdate(self, item: Post):
        return item.created_date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['foo'] = 'bar'
        return context
