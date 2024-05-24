from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from app.settings import MEDIA_URL
from posts.models import Post
from urllib.parse import urljoin


class LatestPostsFeed(Feed):
    title = 'Gamnig Ua'
    description_template = 'posts/feed_description.html'
    link = reverse_lazy('posts:feed')
    description = 'Нові публікації на сайті Gamnig Ua'
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