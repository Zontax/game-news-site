from django.core.validators import RegexValidator
from django.core.files.base import ContentFile

from users.models import User, Profile
import uuid
import requests

username_validator = RegexValidator(
    r'^[\w-]+$',
    "Введіть коректне ім'я користувача. Це значення може містити тільки букви, цифри та символи <b>-_.</b>"
)


def generate_token(prefix: str = '') -> str:
    """
    Згенерувати випадковий UUID код (активація акаунта, зміна паролю).
    :param prefix: об'єкт моделі User.
    """
    return str(f'{prefix}{uuid.uuid4().hex}')


def send_confirmation_email(user: User):
    """Відправити на почту `user` данні про активацію.
    :param user: об'єкт моделі User.
    """
    pass


def create_profile_and_add_avatar(backend, user: User, *args, **kwargs):
    """
    Створити профіль користувача для соціальної аутентифікації
    """
    response = kwargs['response']
    profile, create = Profile.objects.get_or_create(user=user)

    if backend.name == 'google-oauth2' and create:
        if response['picture']:
            url = response['picture']
            response = requests.get(url)
            profile.avatar.save(f'{user.username}.jpg',
                                ContentFile(response.content), save=True)
