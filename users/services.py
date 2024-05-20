from django.core.validators import RegexValidator

from users.models import User
import uuid

username_validator = RegexValidator(r'^[\w-]+$',
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
