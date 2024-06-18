from django.core.management.utils import get_random_secret_key
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.settings.base import MEDIA_ROOT
from main.services import create_random_image
from api.serializers import UserListSerializer, PostListSerializer, PostDetailSerializer
from posts.models import Post, PostType, PostTag, PostTopic, PostComment
from posts.services import post_search

from mimesis import Person, Text, Datetime
from mimesis.builtins import UkraineSpecProvider
from datetime import datetime, timedelta
from pytils.translit import slugify
from random import randint
import logging
import random
import uuid

User = get_user_model()

person = Person('uk')
text = Text('uk')
datetime_gen = Datetime('uk')
ua_provider = UkraineSpecProvider()
tab_text1 = text.text(1)
tab_text2 = text.text(2)
tab_text3 = text.text(4)

logger = logging.getLogger(__name__)


class TestHtmxAPIView(APIView):
    def get(self, request):
        data = {
            'test': 'HTMX',
            'message': 'HTMX Рулить, Test message',
        }
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


class ModalWindowAPIView(APIView):
    def get(self, request: HttpRequest):
        query = request.GET.get('title')
        context = {
            'modal_title': 'Модальнко вікно',
            'modal_body': 'Тестове модальне вікно з текстом',
        }
        return TemplateResponse(request, '_modal_window.html', context)


class DateTimeAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час користувача.
    """

    def get(self, request: HttpRequest):
        data = {
            "datetime": timezone.now().strftime('%d/%m/%Y, %H:%M:%S, %Z%z'),
        }
        return JsonResponse(data)


class ServerDateTimeAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час сервера.
    """

    def get(self, request):
        data = {
            "datetime": datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
            "server-timezone": str(timezone.get_current_timezone())
        }
        return JsonResponse(data)


class IP_APIView(APIView):
    """
    API endpoint, який повертає IP адресс користувача.
    """

    def get(self, request: HttpRequest):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        data = {
            "ip": ip
        }
        return JsonResponse(data)


class HtmxTabsAPIView(APIView):
    """
    API endpoint для пошуку публікацій
    """

    def get(self, request: HttpRequest, text: str):
        
        if text == '2':
            txt = tab_text1
        elif text == '3':
            txt = tab_text2
        else:
            txt = tab_text3
            
        return HttpResponse(f"""
            <div class='form-error'>
                <h4>Вкладка {text}</h4>
                <p>{txt}</p>
            </div>""")


class GenerateKeyAPIView(APIView):
    """
    API endpoint, який генерує секретний ключ.
    """

    def get(self, request: HttpRequest):
        key = get_random_secret_key()
        
        return HttpResponse(str(key))


class DateTimeSecondsAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час сервера.
    """

    def get(self, request: HttpRequest):

        return Response(timezone.now().second)


class SearchPostsAPIView(APIView):
    """
    API endpoint для пошуку публікацій
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

    def get(self, request: HttpRequest):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)

        return Response(serializer.data)


class PostListAPIView(APIView):
    """
    API endpoint, який отримує всі опубліковані публікації.
    """

    def get(self, request: HttpRequest):
        posts = Post.published.all()
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)


class PostDetailAPIView(APIView):
    """
    API endpoint, який отримує відомості про конкретну публікацію.
    """

    def get(self, request: HttpRequest, pk: int):
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

    def get(self, request: HttpRequest, count=2):
        try:
            for i in range(count):
                uid = uuid.uuid4().hex
                date = datetime.now()
                year = date.year
                month = date.month
                day = date.day

                if day < 10:
                    day = f'0{day}'
                if month < 10:
                    month = f'0{month}'

                image_path = f'images/posts/{year}/{month}/{day}/{uid}.png'
                create_random_image(MEDIA_ROOT / image_path)
                print(MEDIA_ROOT / image_path)

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
