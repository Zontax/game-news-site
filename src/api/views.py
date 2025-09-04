import os
import uuid
import random
import logging
from datetime import datetime, timedelta
from django.core.management.utils import get_random_secret_key
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from mimesis import Person, Text, Datetime
from mimesis.builtins import UkraineSpecProvider
from pytils.translit import slugify
from core.settings.base import MEDIA_ROOT, APP_NAME, TOKEN_LIFETIME
from main.services import create_random_image
from users.models import User
from api.serializers import UserListSerializer, PostListSerializer, PostDetailSerializer, UserRegisterSerializer, UserLoginSerializer
from posts.models import Post, PostType, PostTag, PostTopic, PostComment
from posts.services import post_search
from django.contrib.auth import login, logout
from rest_framework.authtoken.models import Token
from rest_framework import status
from users.services import generate_token
from users.tasks import send_to_email, clear_user_token
from django.urls import reverse_lazy


logger = logging.getLogger(__name__)
person = Person('uk')
text = Text('uk')
datetime_gen = Datetime('uk')
ua_provider = UkraineSpecProvider()
tab_text1 = text.text(1)
tab_text2 = text.text(2)
tab_text3 = text.text(4)


class UserRegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_token()
            # Note: The confirmation URL should ideally point to frontend app,
            # which then makes a request to the backend API.
            # For simplicity, we point to the API directly here.
            activation_url = request.build_absolute_uri(
                reverse_lazy('api:register_confirm', kwargs={'token': token}))

            subject = f'Account Activation ({APP_NAME})'
            message = f'({APP_NAME}) Account activation code: {token}'
            html_message = f"""
                    <h2>Account Activation ({APP_NAME})</h2>
                    <p>Your code: <b>{token}</b></p>
                    <p>Or follow the link <a href="{activation_url}">{activation_url}</a></p>"""
            send_to_email.delay(subject, message, html_message, [user.email])

            user.activation_key = token
            user.save()

            clear_user_token.apply_async((user.pk,), countdown=TOKEN_LIFETIME)

            return Response({"message": "User created successfully. Please check your email to activate your account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(
                email=serializer.validated_data['email']).first()
            if user and user.check_password(serializer.validated_data['password']):
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    login(request, user)
                    return Response({'token': token.key}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "User account is not active"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            logout(request)
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class TestHtmxAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest):
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


class ServerDateTimeAPIView(APIView):
    """
    API endpoint, який повертає поточну дату й час сервера.
    """

    def get(self, request: HttpRequest):
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


class FakePostCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: HttpRequest, count: int = 2):
        try:
            for i in range(count):
                uid = uuid.uuid4().hex
                date = datetime.now()
                year = date.year
                month = f"{date.month:02d}"
                day = f"{date.day:02d}"

                image_path = f'images/posts/{year}/{month}/{day}/{uid}.png'
                full_image_path = MEDIA_ROOT / image_path

                os.makedirs(full_image_path.parent, exist_ok=True)
                create_random_image(full_image_path)

                post_types = list(PostType.objects.all())
                if not post_types:
                    return Response({'message': 'Немає типів постів у базі даних'}, status=500)
                type = random.choice(post_types)

                users = list(User.objects.all())
                if not users:
                    return Response({'message': 'Немає користувачів у базі даних'}, status=500)
                user = random.choice(users)

                title = f'Фейковий пост {uid}'[:130]
                slug = slugify(f'{uid}')[:130]
                content = f'Фейковий контент {uid}'

                r_days = random.randint(-3, 3)
                r_hours = random.randint(-12, 12)
                r_date = timezone.now() + timedelta(days=r_days, hours=r_hours)

                post = Post.objects.create(
                    user=user,
                    type=type,
                    title=title,
                    slug=slug,
                    content=content,
                    image=image_path,
                    created_date=r_date,
                )

                if type.slug == 'reviews':
                    post.review_rating = random.randint(10, 98)
                    post.review_pluses = 'Плюси: гарний дизайн'
                    post.review_minuses = 'Мінуси: висока ціна'
                    post.save()

                for _ in range(random.randint(1, 5)):
                    PostComment.objects.create(
                        post=post,
                        user=user,
                        text='Це тестовий коментар.',
                        created_date=r_date,
                    )

                # Додавання тем, якщо вони є
                topics = list(PostTopic.objects.all())
                if topics:
                    for _ in range(2):
                        post.topics.add(random.choice(topics))

                # Додавання тегів, якщо вони є
                tags = list(PostTag.objects.all())
                if tags:
                    for _ in range(6):
                        post.tags.add(random.choice(tags))

            serializer = PostDetailSerializer(post)
            return Response(serializer.data)

        except Exception as e:
            data = {
                'message': 'Помилка при створенні публікацій',
                'error': str(e)
            }
            logger.error(e)
            return Response(data, status=500)


class CheckUsernameAPIView(APIView):
    """
    API endpoint, який перевіряє чи є користувач з таким username
    """

    def get(self, request: HttpRequest):
        username = request.GET['username'].strip()

        if username.__len__() == 0:
            return HttpResponse()
        elif username.__len__() < 2:
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
