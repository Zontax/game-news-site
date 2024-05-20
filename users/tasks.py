from celery import shared_task
from django.core.mail.message import EmailMultiAlternatives

from users.models import User


@shared_task
def clear_activation_key(user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.activation_key = None
        user.save()
        print(f'Секретний ключ {user.username} очищено')
    except User.DoesNotExist:
        print('User does not exist')


@shared_task
def send_email_to(subject, body, from_email, to_email):
    try:
        email = EmailMultiAlternatives(subject, body, from_email, [to_email])
        email.content_subtype = 'html'
        email.send()
    except:
        pass
