from django.db.models import Count, Prefetch, Q
from django.http import Http404, HttpRequest, HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View, ListView, DetailView, DeleteView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.forms import CreatePostCommentForm
from posts.models import Post, PostType, PostTopic, PostTag, PostComment
from posts.services import post_search
from app.settings import POSTS_IN_PAGE, CKEDITOR_5_CONFIGS
import logging

logger = logging.getLogger(__name__)


class PostListView(View):

    def get(self, request: HttpRequest, type_slug=None, tag_slug=None, topic_slug=None):
        page = request.GET.get('page', 1)
        query = request.GET.get('q', '')
        topic_param = request.GET.get('topic', None)
        type = None
        topic = None
        tag = None

        if tag_slug:
            posts = Post.published.filter(tags__slug=tag_slug)
            tag = PostTag.objects.get(slug=tag_slug)
        elif topic_slug:
            posts = Post.published.filter(topics__slug=topic_slug)
            topic = PostTopic.objects.get(slug=topic_slug)
        elif (type_slug == None and query == ''):
            posts = Post.published.all()
        elif query:
            posts = post_search(query)
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
            'posts': posts,
            'type': type,
            'topics': topics,
            'slug_url': type_slug,
            'topic': topic,
            'tag': tag,
            'query': query,
        }
        return render(request, 'posts/index.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    queryset = (Post.published
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
        form = CreatePostCommentForm(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                text = form.cleaned_data['text']

                PostComment.objects.create(
                    user=request.user,
                    post=post,
                    text=text
                )
                messages.success(request, f'Коментар {text} створено')
            else:
                messages.error(request, 'Увійдіть щоб писати коментарі.')

        return redirect(post)

    def get_context_data(self, **kwargs):

        latest_posts = (Post.published
                        .filter(type=self.object.type)[:5]
                        .select_related('type', 'user')
                        .annotate(comment_count=Count('comments',
                                                      Q(comments__is_active=True)))
                        )

        post: Post = self.get_object(self.queryset)
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = (Post.published
                         .filter(tags__in=post_tags_ids)
                         .exclude(id=post.id).annotate(same_tags=Count('tags'))
                         .order_by('-same_tags')[:4]
                         )
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['latest_posts'] = latest_posts
        context['similar_posts'] = similar_posts
        context['ckeditor_comments_config'] = CKEDITOR_5_CONFIGS['comments']
        context['form'] = CreatePostCommentForm()
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


class DeletePostView(View):

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


class DeletePostCommentView(View):

    def get(self, request: HttpRequest, id):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Ви не увійшли в систему')

        try:
            comment = PostComment.objects.get(id=id)

        except PostComment.DoesNotExist:
            return Http404('Коментар не знайдено. Схоже, що він вже видалений.')

        comment.delete()
        messages.success(request, f'Коментар ({id}) видалено')

        return redirect(reverse('posts:detail', args=[comment.post.slug]) + '#comments')


class PostLikeAPIView(APIView):
    """
    API endpoint для додавання користувачем лайків на публікацію.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            data = f'<i class="bi bi-plus-square"></i> {post.likes.count()}'
        else:
            post.likes.add(user)
            if post.dislikes.filter(id=user.id).exists():
                post.dislikes.remove(user)
            data = f'<i class="bi bi-plus-square-fill"></i> {post.likes.count()}'

        return HttpResponse(data)


class PostDislikeAPIView(APIView):
    """
    API endpoint для додавання користувачем дизлайків на публікацію.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.dislikes.filter(id=user.id).exists():
            post.dislikes.remove(user)
            data = f'<i class="bi bi-dash-square"></i> {post.dislikes.count()}'
        else:
            post.dislikes.add(user)
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
            data = f'<i class="bi bi-dash-square-fill"></i> {post.dislikes.count()}'

        return HttpResponse(data)



class PostSaveAPIView(APIView):
    """
    API endpoint для додання публікаціїї у "збережені" користувачів.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.saves.filter(id=user.id).exists():
            post.saves.remove(user)
            data = f'<i class="bi bi-bookmark"></i> {post.saves.count()}'
        else:
            post.saves.add(user)
            data = f'<i class="bi bi-bookmark-check-fill"></i> {post.saves.count()}'

        return HttpResponse(data)
