from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserListSerializer, PostListSerializer, PostDetailSerializer
from main.services import create_random_image
from posts.models import Post, PostType, PostTag, PostTopic, PostComment
from users.models import User
from posts.services import q_search

from mimesis import Person, Text, Datetime
from mimesis.builtins import UkraineSpecProvider
from datetime import datetime, timedelta, UTC
from random import randint
from pytils.translit import slugify
from app.settings import BASE_DIR
import logging
import random
import uuid

person = Person('uk')
text = Text('uk')
datetime_gen = Datetime('uk')
ua_provider = UkraineSpecProvider()

logger = logging.getLogger(__name__)


class TestHtmxAPIView(APIView):
    """
    API endpoint that returns a test JSON response.
    This API view is used for HTMX testing.
    """

    def get(self, request):

        json_data = {
            'test': 'HTMX',
            'message': 'HTMX Рулить, Test message',
        }
        return JsonResponse(json_data, json_dumps_params={'ensure_ascii': False})


class DateTimeAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час сервера.
    """

    def get(self, request):

        json_data = {
            "datetime": timezone.now().strftime('%d/%m/%Y, %H:%M:%S'),
        }
        return JsonResponse(json_data)


class SearchPostsAPIView(APIView):
    """
    API endpoint that searches posts based on a query.
    """

    def get(self, request: HttpRequest):

        query = request.GET['q']

        posts = (q_search(query)
                 .filter(is_publicated=True)
                 .select_related('type', 'user')
                 .annotate(comment_count=Count('comments')))

        return TemplateResponse(request, 'posts/_posts_list.html', {'posts': posts})


class GetReplyCommentsAPIView(APIView):
    """
    API endpoint that retrieves reply comments for a specific comment.
    """

    def get(self, request: HttpRequest, id):
        replies = PostComment.objects.filter(parent_id=id).order_by(
            'created_date').annotate(replies_count=Count('replies'))

        return TemplateResponse(request, 'posts/_comment_tree.html', {'comments': replies})


class PostLikeAPIView(APIView):
    """
    API endpoint для додавання користувачем лайків на публікацію.
    """

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user: User = request.user

        if user.is_authenticated:
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
            else:
                post.likes.add(user)
                if post.dislikes.filter(id=user.id).exists():
                    post.dislikes.remove(user)

            data = f'➕ {post.likes.count()}'
        else:
            data = '➕ Зареєструйтесь'

        return HttpResponse(data)


class PostDislikeAPIView(APIView):
    """
    API endpoint для додавання користувачем дизлайків на публікацію.
    """

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user: User = request.user

        if user.is_authenticated:
            if post.dislikes.filter(id=user.id).exists():
                post.dislikes.remove(user)
            else:
                post.dislikes.add(user)
                if post.likes.filter(id=user.id).exists():
                    post.likes.remove(user)

            return HttpResponse(f'➖ {post.dislikes.count()}')

        return HttpResponse('➖ Зареєструйтесь')


class PostSaveAPIView(APIView):
    """
    API endpoint для додання публікаціїї у "збережені" користувачів.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest, post_id):
        post = get_object_or_404(Post, id=post_id)
        user: User = request.user

        if user.is_authenticated:
            if post.saves.filter(id=user.id).exists():
                post.saves.remove(user)
                data = f'<i class="bi bi-bookmark"></i> {post.saves.count()}'
            else:
                post.saves.add(user)
                data = f'<i class="bi bi-bookmark-check-fill"></i> {post.saves.count()}'
        else:
            data = '<i class="bi bi-bookmark"></i> Зареєструйтесь'

        return HttpResponse(data)


class UserListAPIView(APIView):
    """
    API endpoint, який отримує всіх користувачів.
    """

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)

        return Response(serializer.data)


class PostListAPIView(APIView):
    """
    API endpoint, який отримує всі опубліковані публікації.
    """

    def get(self, request):
        posts = Post.published.all()
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)


class PostDetailAPIView(APIView):
    """
    API endpoint, який отримує відомості про конкретну публікацію.
    """

    def get(self, request, pk: int):
        post = Post.objects.get(id=pk)
        serializer = PostDetailSerializer(post)

        return Response(serializer.data)


class PostCreateAPIView(APIView):
    """
    API endpoint, який створює нову публікацію.
    """

    def post(self, request: HttpRequest):
        try:
            post = Post.objects.create(
                type=PostType.objects.get(id=request.data['type_id']),
                title=request.data['title'],
                slug=request.data['slug'],
                content=request.data['content'],
                image=request.data['image'],
                created_date=timezone.now(),
            )
            serializer = PostDetailSerializer(post)
            Response(serializer.data)

        except Exception as e:
            data = {
                'message': 'Помилка при створенні поста',
                'error': str(e)
            }
            return Response(data, 500)


def is_admin(user):
    return user.is_superuser


@method_decorator(user_passes_test(is_admin), name='dispatch')
class FakePostCreateAPIView(APIView):
    """
    API endpoint, який створює публікації для тестування роботи сайту.
    """

    def get(self, request: HttpRequest, count=5):
        try:
            for i in range(count):
                uid = uuid.uuid4().hex
                image_path = f'images/posts_title/{uid}.png'
                full_image_path = str(BASE_DIR / 'media/' / image_path)

                create_random_image(full_image_path)

                title = f'{text.title()[:80]} {uid}'[:130]
                slug = slugify(f'{uid}')[:130]
                content = f'{text.text(20)}\nfake post'

                r_days = randint(-3, 3)
                r_hours = randint(-12, 12)
                r_date = datetime.now(
                    UTC) + timedelta(days=r_days, hours=r_hours)

                type = random.choice(PostType.objects.all())
                
                # Create fake post
                post = Post.objects.create(
                    user=random.choice(User.objects.all()[1:]),
                    type=type,
                    title=title,
                    slug=slug,
                    content=content,
                    image=image_path,
                    created_date=r_date,
                )
                
                if type.id == 2:
                    post.review_rating = randint(10, 98)
                    post.review_pluses = text.title()
                    post.review_minuses = text.title()
                    post.save()

                # Create fake comments
                for i in range(randint(1, 5)):
                    PostComment.objects.create(
                        post=post,
                        user=random.choice(User.objects.all()[1:]),
                        text=text.title(),
                        created_date=r_date,
                    )

                # Add topics and tags
                for i in range(2):
                    topic = random.choice(PostTopic.objects.all())
                    post.topics.add(topic)

                for i in range(6):
                    tag = random.choice(PostTag.objects.all())
                    post.tags.add(tag)

            serializer = PostDetailSerializer(post)
            return Response(serializer.data)

        except Exception as e:
            data = {
                'message': 'Помилка при створенні публікацій',
                'error': str(e)
            }
            logger.error(e)
            return Response(data, 500)
