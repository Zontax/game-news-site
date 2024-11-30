from django.urls import reverse, resolve
from django.test import TestCase, RequestFactory as RF

from posts.views import PostListView, PostDetailView, SavedPostListView, RandomPostsView


class TestMainUrls(TestCase):

    def test_post_index_url(self):
        self.assertEqual(reverse('posts:index'), '/posts/')
        self.assertEqual(resolve('/posts/').func.view_class, PostListView)

    def test_post_search_url(self):
        search_path = RF().get('/posts/search?q=microsoft+store').path_info

        self.assertEqual(reverse('posts:search'), '/posts/search')
        self.assertEqual(resolve('/posts/search').func.view_class,
                         PostListView)
        self.assertEqual(resolve(search_path).func.view_class,
                         PostListView)

    def test_post_type_url(self):
        url = reverse('posts:type', kwargs=['news'])

        self.assertEqual(url, '/posts/news/')
        self.assertEqual(resolve(url).func.view_class, PostListView)

    def test_post_tag_url(self):
        url = reverse('posts:tag', args=['some-tag'])

        self.assertEqual(url, '/posts/tag/some-tag/')
        self.assertEqual(resolve(url).func.view_class, PostListView)

    def test_detail_url(self):
        url = reverse('posts:detail', args=['some-post-slug'])

        self.assertEqual(url, '/posts/detail/some-post-slug/')
        self.assertEqual(resolve(url).func.view_class, PostDetailView)
