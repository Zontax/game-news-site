from django.core.cache import cache
from django.core.mail import send_mail
from celery import shared_task
from redis import Redis
from core.settings.base import EMAIL_HOST_USER
from users.models import User


@shared_task
def clear_user_token(user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.activation_key = None
        user.save()
        return 'ok'
    except User.DoesNotExist:
        return 'error'


@shared_task
def send_to_email(subject, message, html_message, to_email, fail_silently=False):
    try:
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=fail_silently)
        return 'ok'
    except Exception as e:
        return 'error'
