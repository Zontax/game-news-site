from django.db.models import Count, Prefetch, Q
from django.http import Http404, HttpRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View, DetailView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from app.settings.base import POSTS_IN_PAGE, REDIS_HOST, REDIS_PORT, REDIS_DB
from posts.forms import CreatePostCommentForm
from posts.models import Post, PostType, PostTopic, PostTag, PostComment
from posts.services import post_search
from redis import Redis
import logging

logger = logging.getLogger(__name__)


redis = Redis(host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB)


class PostListView(View):

    def get(self, request: HttpRequest, type_slug=None, tag_slug=None, topic_slug=None):
        page = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        topic_param = request.GET.get('topic', None)
        latest_posts = None
        type = None
        topic = None
        tag = None

        if tag_slug:
            posts = Post.published.filter(tags__slug=tag_slug)
            tag = PostTag.objects.get(slug=tag_slug)
        elif topic_slug:
            posts = Post.published.filter(topics__slug=topic_slug)
            topic = PostTopic.objects.get(slug=topic_slug)
        elif (type_slug == None and search_query == ''):
            posts = Post.published.all()
        elif search_query:
            posts = post_search(search_query)
            latest_posts = (Post.published.all()[:5]
                            .select_related('type', 'user')
                            .annotate(comment_count=Count('comments', Q(comments__is_active=True)))
                            )
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
            'posts': posts,
            'latest_posts': latest_posts,
            'type': type,
            'topics': topics,
            'slug_url': type_slug,
            'topic': topic,
            'tag': tag,
        }
        if type:
            context['title'] = type.name
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
                messages.success(request, f'Ваш коментар опубліковано')
            else:
                messages.error(request, 'Увійдіть щоб писати коментарі.')

        return redirect(post)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post: Post = self.get_object(self.queryset)

        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = (Post.published
                         .filter(tags__in=post_tags_ids)
                         .exclude(id=post.id)
                         .annotate(same_tags=Count('tags'))
                         .order_by('-same_tags')[:5]
                         )
        latest_posts = (Post.published
                        .filter(type=self.object.type)[:5]
                        .select_related('type', 'user')
                        .annotate(comment_count=Count('comments', Q(comments__is_active=True)))
                        )
        total_views = redis.incrby(f'post:{post.id}:views')
        total_rating = redis.zincrby('post_ranking', 1, post.id)

        context['total_views'] = total_views
        context['total_rating'] = total_rating
        context['latest_posts'] = latest_posts
        context['similar_posts'] = similar_posts
        context['form'] = CreatePostCommentForm()
        return context


class SavedPostListView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        page = request.GET.get('page', 1)
        posts = (Post.published
                 .filter(saves=request.user.id)
                 .select_related('type', 'user')
                 .annotate(comment_count=Count('comments'))
                 )
        paginator = Paginator(posts, POSTS_IN_PAGE)
        posts_in_page = paginator.page(int(page))

        context = {
            'title': 'Збережені',
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
            Post.objects.get(slug=post_slug).delete()
        except Post.DoesNotExist:
            raise Http404(
                'Публікацію не знайдено. Схоже, що вона вже видалена.')

        messages.success(request, f'Публікацію ({post_slug}) видалено')

        return redirect(reverse('main:index'))


class DeletePostCommentView(View):

    def get(self, request: HttpRequest, id):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Ви не увійшли на сайт')

        try:
            comment = PostComment.objects.get(id=id)

        except PostComment.DoesNotExist:
            return Http404('Коментар не знайдено.')

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
            data = f'<block title="Поставити лайк"><i class="bi bi-plus-square"></i> Лайк {post.likes.count()}</block>'
        else:
            post.likes.add(user)
            if post.dislikes.filter(id=user.id).exists():
                post.dislikes.remove(user)
            data = f'<block title="Зняти лайк"><i class="bi bi-plus-square-fill"></i> Лайк {post.likes.count()}</block>'

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
            data = f'<block title="Поставити дизлайк"><i class="bi bi-dash-square"></i> {post.dislikes.count()} Дизлайк</block>'
        else:
            post.dislikes.add(user)
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
            data = f'<block title="Зняти дизлайк"><i class="bi bi-dash-square-fill"></i> {post.dislikes.count()} Дизлайк</block>'

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
            data = f'<block title="Додати в збережені"><i class="bi bi-bookmark"></i></block>'
        else:
            post.saves.add(user)
            data = f'<block title="Вилучити зі збережених"><i class="bi bi-bookmark-check-fill"></i></block>'

        return HttpResponse(data)


class ScrollPostListView(View):

    def get(self, request: HttpRequest):
        page = int(request.GET.get('p', 1))
        posts = (Post.published.all()
                 .select_related('type', 'user')
                 .annotate(comment_count=Count('comments')))
        paginator = Paginator(posts, POSTS_IN_PAGE)

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {
            'posts': posts,
            'scroll_next_page': page + 1,
            'scroll_last_page': (page + 1) > paginator.num_pages
        }
        return TemplateResponse(request, 'posts/_posts_list.html', context)
