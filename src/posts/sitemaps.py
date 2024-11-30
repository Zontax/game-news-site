from django.contrib.sitemaps import Sitemap

from posts.models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj: Post):
        return obj.edit_date
