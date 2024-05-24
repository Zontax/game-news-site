from django.db.models import Model, CharField, TextField, ImageField, DateTimeField, DateField, EmailField, OneToOneField, CASCADE
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from app.settings import AUTH_USER_MODEL
from phonenumber_field.modelfields import PhoneNumberField


def user_avatar_path(instance: 'User', filename):
    return f'images/users/{instance.id}/avatar/{filename}'


def user_profile_bg_path(instance: 'User', filename):
    return f'images/users/{instance.id}/profile_bg/{filename}'


class User(AbstractUser):
    """
    Базова повнофункціональна модель користувача в системі.
    """
    username = CharField(
        _('Username'),
        max_length=40,
        unique=True,
        help_text=_(
            'Required. 40 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[ASCIIUsernameValidator(), MinLengthValidator(3)],
        error_messages={'unique': _(
            'A user with that username already exists.'), },
    )
    email = EmailField('Пошта Email', unique=True)
    description = TextField('Опис профілю', max_length=500,
                            blank=True, null=True)
    birthday_date = DateTimeField('День народження',
                                  blank=True, null=True)
    phone_number = PhoneNumberField('Номер телефону', region='UA',
                                    blank=True, null=True)
    avatar = ImageField('Аватар', upload_to=user_avatar_path,
                        blank=True, null=True)
    profile_bg = ImageField('Фон', upload_to=user_profile_bg_path,
                            blank=True, null=True)
    activation_key = CharField('Секретний код', max_length=80,
                               blank=True, null=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta():
        db_table = 'users'
        verbose_name = 'Користувач'
        verbose_name_plural = '🔴 Користувачі'
        ordering = ('date_joined',)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user:detail', args=[self.username])


# class Profile(Model):
#     user = OneToOneField(AUTH_USER_MODEL, on_delete=CASCADE)
#     date_of_birth = DateField(blank=True, null=True)
#     photo = ImageField(upload_to='users/%Y/%m/%d/', blank=True)

#     class Meta():
#         db_table = 'profiles'
#         verbose_name = 'Профіль'
#         verbose_name_plural = '🟥 Профілі'
#         ordering = ('date_joined',)

#     def __str__(self):
#         return f'Профіль [{self.user.username}]'
