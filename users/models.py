from django.db.models import CharField, TextField, ImageField, DateTimeField, EmailField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


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
    description = TextField(
        'Опис профілю', max_length=500, blank=True, null=True)
    birthday_date = DateTimeField('День народження',
                                  blank=True, null=True)
    phone_number = PhoneNumberField(
        'Номер телефону', region='UA', blank=True, null=True)
    avatar = ImageField(
        'Аватар', upload_to='images/users/avatar', blank=True, null=True)
    profile_bg = ImageField(
        'Фон', upload_to='images/users/profile_bg', blank=True, null=True)
    activation_key = CharField(
        'Секретний код', max_length=80, blank=True, null=True)

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
        return reverse('user:detail', kwargs={'username': self.username})
