from django.db.models import Count, Prefetch, Q
from django.http import Http404, HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View, ListView, DetailView, DeleteView

from posts.models import Post, PostType, PostTopic, PostComment
from posts.services import q_search
from app.settings import POSTS_IN_PAGE
import logging

logger = logging.getLogger(__name__)


class PostListView(View):

    def get(self, request: HttpRequest, type_slug=None, tag_slug=None, topic_slug=None):
        page = request.GET.get('page', 1)
        query = request.GET.get('q', '')
        topic_param = request.GET.get('topic', None)
        type = None
        topic = None

        if tag_slug:
            posts = Post.published.filter(tags__slug=tag_slug)
        elif topic_slug:
            posts = Post.published.filter(topics__slug=topic_slug)
            topic = PostTopic.objects.get(slug=topic_slug)
        elif (type_slug == None and query == ''):
            posts = Post.published.all()
        elif query:
            posts = q_search(query)
        else:
            type = get_object_or_404(PostType, slug=type_slug)
            if topic_param:
                posts = Post.published.filter(type=type,
                                              topics__slug=topic_param)
                topic = PostTopic.objects.get(slug=topic_param)
            else:
                posts = Post.published.filter(type=type)

        posts = (posts.select_related('type', 'user')
                 .annotate(comment_count=Count('comments')))

        topics = PostTopic.objects.filter(is_general=True)
        paginator = Paginator(posts, POSTS_IN_PAGE)

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {
            'title': 'Каталог',
            'type': type,
            'posts': posts,
            'topics': topics,
            'slug_url': type_slug,
            'topic': topic,
            'query': query,
        }
        return render(request, 'posts/index.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    queryset = (Post.published
                .annotate(comment_count=Count('comments', Q(comments__is_active=True)))
                .prefetch_related(
                    Prefetch('comments', PostComment.active
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
        latest_posts = (Post.published
                        .filter(type=self.object.type)[:5]
                        .select_related('type', 'user')
                        .annotate(comment_count=Count('comments'))
                        )
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['latest_posts'] = latest_posts
        return context


class SavedPostListView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        page = request.GET.get('page', 1)
        user_id = request.user.id

        posts = (Post.published
                 .filter(saves=user_id)
                 .select_related('type', 'user')
                 .annotate(comment_count=Count('comments'))
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
            Post.published
            .order_by('?')
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments'))
        )

        context = {
            'posts': posts,
        }
        return render(request, 'main/index.html', context)


class DeletePostsView(View):

    def get(self, request: HttpRequest, post_slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Ви не увійшли в систему')

        try:
            post = Post.objects.get(slug=post_slug)

        except Post.DoesNotExist:
            return Http404('Публікацію не знайдено. Схоже, що вона вже видалена.')

        post.delete()
        messages.success(request, f'Публікацію ({post_slug}) видалено')

        return redirect(reverse('main:index'))

# import os
# from urllib.parse import urljoin
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# class Ckeditor5Storage(FileSystemStorage):
#     """Custom storage for django_ckeditor_5 images."""

#     location = os.path.join(MEDIA_ROOT, "django_ckeditor_5")
#     base_url = urljoin(MEDIA_URL, "django_ckeditor_5/")
