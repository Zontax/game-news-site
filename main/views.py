from django.shortcuts import render
from django.http import BadHeaderError, HttpRequest, JsonResponse
from django.db.models import Count
from django.views import View
from django.core.mail import send_mail
import django

from app.settings import APP_NAME, EMAIL_HOST_USER
from posts.models import Post
from smtplib import SMTPException
from pytils.translit import slugify
import logging

logger = logging.getLogger(__name__)


class IndexView(View):

    def get(self, request: HttpRequest):
        posts = (
            Post.objects
            .filter(is_publicated=True)
            .order_by('-created_date')[:8]
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments')))

        latest_posts = (
            Post.objects
            .filter(type__name='Огляди', is_publicated=True)[:5]
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments')))

        context = {
            'posts': posts,
            'latest_posts': latest_posts
        }
        return render(request, 'main/index.html', context)


class AboutView(View):

    def get(self, request: HttpRequest):
        context = {
            'title': 'Про сайт',
            'description': f'Це шаблон сайта новин Django {django.get_version()}',
        }
        return render(request, 'main/about.html', context)


class TestEmailView(View):

    def get(self, request: HttpRequest):
        try:
            send_mail(
                subject=f'({APP_NAME}) ТЕСТ',
                message='',
                html_message=f"""<h1>({APP_NAME}) ТЕСТ</h1>""",
                from_email=EMAIL_HOST_USER,
                recipient_list=[EMAIL_HOST_USER],
                fail_silently=False)
        except (BadHeaderError, SMTPException) as ex:
            logger.error('email error')
            return JsonResponse({'success': False,
                                 'error': f'Не вдалося відправити електронний лист. {ex}'})
        return JsonResponse({'success': True})
