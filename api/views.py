from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.settings import MEDIA_ROOT
from main.services import create_random_image
from api.serializers import UserListSerializer, PostListSerializer, PostDetailSerializer
from posts.models import Post, PostType, PostTag, PostTopic, PostComment
from posts.services import post_search

from mimesis import Person, Text, Datetime
from mimesis.builtins import UkraineSpecProvider
from datetime import timedelta
from random import randint
from pytils.translit import slugify

import logging
import random
import uuid

User = get_user_model()

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


class DateTimeSecondsAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час сервера.
    """

    def get(self, request):

        return Response(timezone.now().second)


class SearchPostsAPIView(APIView):
    """
    API endpoint that searches posts based on a query.
    """

    def get(self, request: HttpRequest):

        query = request.GET['q']

        posts = (post_search(query)
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


# @method_decorator(user_passes_test(is_admin), name='dispatch')
class FakePostCreateAPIView(APIView):
    """
    API endpoint, який створює публікації для тестування роботи сайту.
    """
    permission_classes = [IsAdminUser]

    def get(self, request: HttpRequest, count=5):
        try:
            for i in range(count):
                uid = uuid.uuid4().hex
                date = timezone.now()
                month = date.month
                day = date.day

                if day < 10:
                    day = f'0{day}'
                if month < 10:
                    month = f'0{month}'

                image_path = f'images/posts/{date.year}/{month}/{day}/{uid}.png'
                create_random_image(MEDIA_ROOT / image_path)
                print(image_path)

                title = f'{text.title()[:80]} {uid}'[:130]
                slug = slugify(f'{uid}')[:130]
                content = f'{text.text(20)}\nfake post'

                r_days = randint(-3, 3)
                r_hours = randint(-12, 12)
                r_date = timezone.now() + timedelta(days=r_days, hours=r_hours)

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


class CheckUsernameAPIView(APIView):
    """
    API endpoint, який перевіряє чи є користувач з таким username
    """

    def get(self, request: HttpRequest):
        username = request.GET['username'].strip()
        
        if username.__len__() == 0:
            return HttpResponse()
        elif username.__len__() < 3:
            return HttpResponse(f"<div id='check-username' class='form-error'>Закоротке ім'я {username.__len__()}</div>")
        
        if User.objects.filter(username=username).exists():
            data = "<div id='check-username' class='form-error'>Це ім'я зайняте</div>"
        else:
            data = "<div id='check-username' class='form-success'>Ім'я вільне</div>"

        return HttpResponse(data)


class CheckEmailAPIView(APIView):
    """
    API endpoint, який перевіряє чи є користувач з таким email
    """

    def get(self, request: HttpRequest):
        email = request.GET['email'].strip()
        
        if User.objects.filter(email=email).exists() and email != '':
            return HttpResponse("<div class='form-error'>Користувач з таким email вже існує</div>")
        
        return HttpResponse()
