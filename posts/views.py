from django.db.models import Count, Prefetch, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import View, ListView, DetailView, DeleteView
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from rest_framework.views import APIView
from rest_framework.response import Response


from posts.models import Post, PostType, PostTopic, PostComment
from posts.services import q_search
from app.settings import POSTS_IN_PAGE, BASE_DIR
import logging
import os

logger = logging.getLogger(__name__)


class PostListView(View):

    def get(self, request: HttpRequest, type_slug=None, tag_slug=None, topic_slug=None):
        page = request.GET.get('page', 1)
        query = request.GET.get('q', '')
        topic = request.GET.get('topic', None)
        type = None

        if tag_slug:
            posts = Post.objects.filter(
                tags__slug=tag_slug, is_publicated=True)
        elif topic_slug:
            posts = Post.objects.filter(
                topics__slug=topic_slug, is_publicated=True)
        elif (type_slug == None and query == ''):
            posts = Post.objects.filter(is_publicated=True)
        elif query:
            posts = q_search(query).filter(is_publicated=True)
        else:
            type = get_object_or_404(PostType, slug=type_slug)
            if topic:
                posts = Post.objects.filter(type=type,
                                            topics__slug=topic,
                                            is_publicated=True)
            else:
                posts = Post.objects.filter(type=type,
                                            is_publicated=True)

        posts = (posts.order_by('-created_date')
                 .select_related('type', 'user')
                 .annotate(
            comment_count=Count('comments')))
        topics = PostTopic.objects.filter(is_general=True)

        paginator = Paginator(posts, POSTS_IN_PAGE)

        posts_in_page = paginator.page(int(page))

        context = {
            'title': 'Каталог',
            'type': type,
            'posts': posts_in_page,
            'topics': topics,
            'slug_url': type_slug,
            'query': query,
        }
        return render(request, 'posts/index.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    queryset: QuerySet = (Post.objects
                          .filter(is_publicated=True)
                          .annotate(comment_count=Count('comments'))
                          .prefetch_related(
                              Prefetch('comments', PostComment.objects
                                       .select_related('user')
                                       .filter(parent__isnull=True)
                                       .annotate(replies_count=Count('childrens')))
                          ))

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        post = self.get_object(self.queryset)
        comment_text = request.POST.get('comment_text')

        if post and comment_text:
            if request.user.is_authenticated:
                PostComment.objects.create(
                    post=post,
                    user=request.user,
                    text=comment_text
                )
            else:
                messages.error(request, 'Увійдіть щоб писати коментарі.')

        return redirect(post)

    def get_context_data(self, **kwargs):
        latest_posts = (
            Post.objects
            .filter(type=self.object.type, is_publicated=True)[:5]
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments'))
        )
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['latest_posts'] = latest_posts
        return context


@method_decorator(login_required, name='dispatch')
class SavedPostListView(View):

    def get(self, request: HttpRequest):
        page = request.GET.get('page', 1)
        user_id = request.user.id

        posts: QuerySet[Post] = (Post.objects
                                 .filter(is_publicated=True, saves__id=user_id)
                                 .select_related('type', 'user')
                                 .annotate(comment_count=Count('comments'))
                                 .order_by('-created_date')
                                 )
        paginator = Paginator(posts, POSTS_IN_PAGE)
        posts_in_page = paginator.page(int(page))

        context = {
            'title': 'Каталог',
            'posts': posts_in_page,
        }
        return render(request, 'posts/saved_posts.html', context)


class RandomPostsView(View):

    def get(self, request: HttpRequest):
        posts = (
            Post.objects
            .filter(is_publicated=True)
            .order_by('?')
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments'))
        )

        context = {
            'posts': posts,
        }
        return render(request, 'main/index.html', context)


@method_decorator(login_required, name='dispatch')
class DeletePostsView(View):

    def get(self, request: HttpRequest, post_slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Ви не увійшли в систему')

        try:
            post = Post.objects.get(slug=post_slug)

        except Post.DoesNotExist:
            return HttpResponseNotFound('Публікацію не знайдено. Схоже, що вона вже видалена.')

        post.delete()
        messages.success(request, f'Публікацію ({post_slug}) видалено')

        # reverse('posts:type', args=['news'])
        return redirect(reverse('main:index'))

# import os
# from urllib.parse import urljoin
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# class Ckeditor5Storage(FileSystemStorage):
#     """Custom storage for django_ckeditor_5 images."""

#     location = os.path.join(MEDIA_ROOT, "django_ckeditor_5")
#     base_url = urljoin(MEDIA_URL, "django_ckeditor_5/")
