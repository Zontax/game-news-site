from django.http import BadHeaderError, HttpRequest, HttpResponseNotFound, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views import View
from django.core.management.utils import get_random_secret_key
from django.core.mail import send_mail
import django

from app.settings.base import APP_NAME, SITE_SUPPORT_EMAIL, POSTS_IN_PAGE, EMAIL_HOST_USER
from main.forms import DecodeTextForm
from posts.models import Post
from smtplib import SMTPException
import logging

from users.models import User

logger = logging.getLogger(__name__)


class IndexView(View):

    def get(self, request: HttpRequest):
        posts = (Post.published.all()[:POSTS_IN_PAGE]
                 .select_related('type', 'user')
                 .annotate(comment_count=Count('comments')))

        latest_posts = (
            Post.published.filter(type__name='Огляди')[:5]
            .select_related('type', 'user')
            .annotate(comment_count=Count('comments',
                                          Q(comments__is_active=True)))
        )

        context = {
            'posts': posts,
            'latest_posts': latest_posts,
            'scroll_next_page': 2
        }
        return render(request, 'main/index.html', context)


class AboutView(View):

    def get(self, request: HttpRequest):
        context = {
            'support_email': SITE_SUPPORT_EMAIL,
        }
        return render(request, 'main/about.html', context)


class NotFoundView(View):
    
    def get(self, request: HttpRequest):
        return HttpResponseNotFound()


class TestFunctionsView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest):
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute('SELECT version()')
            db_version = cursor.fetchone()[0]

        dj_version = django.get_version()
        context = {
            'dj_version': dj_version,
            'db_version': db_version,
        }
        return render(request, 'main/test_functions.html', context)


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


class DecodeTextView(FormView):
    template_name = 'main/decode_text.html'
    form_class = DecodeTextForm
    success_url = reverse_lazy('main:decode_text')

    def form_valid(self, form: DecodeTextForm):
        text: str = form.cleaned_data['text']
        in_encoding: str = form.cleaned_data['in_encoding']
        out_encoding: str = form.cleaned_data['out_encoding']

        try:
            ...
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            form.add_error(None, f'Помилка під час декодування тексту: {e}')
            return self.form_invalid(form)

        context = {
            'form': form,
            'decoded_text': text
        }
        return render(self.request, self.template_name, context)
