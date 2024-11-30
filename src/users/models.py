from django.db.models import Model, Index, ForeignKey, ManyToManyField, CharField, TextField, ImageField, DateField, DateTimeField, EmailField, OneToOneField, CASCADE
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse

from core.settings.base import AUTH_USER_MODEL
from phonenumber_field.modelfields import PhoneNumberField


def user_avatar_path(instance: 'User', filename):
    return f'images/users/{instance.user.id}/avatar/{filename}'


def user_profile_bg_path(instance: 'User', filename):
    return f'images/users/{instance.user.id}/profile_bg/{filename}'


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
    activation_key = CharField('Секретний код', max_length=80,
                               blank=True, null=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta():
        db_table = 'users'
        verbose_name = 'Користувач'
        verbose_name_plural = '🔴 Користувачі'
        ordering = ['date_joined']

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user:detail', args=[self.username])


class Profile(Model):
    user = OneToOneField(AUTH_USER_MODEL, on_delete=CASCADE,
                         related_name='profile', verbose_name='Користувач')
    description = TextField('Опис профілю', max_length=500, blank=True, null=True)
    phone_number = PhoneNumberField('Номер телефону', region='UA',
                                    blank=True, null=True)
    date_of_birth = DateField('День народження', blank=True, null=True)
    avatar = ImageField('Аватар', upload_to=user_avatar_path,
                        blank=True, null=True)
    profile_bg = ImageField('Фон', upload_to=user_profile_bg_path,
                            blank=True, null=True)
    following = ManyToManyField('self',
                                through='Subscribe',
                                related_name='followers',
                                symmetrical=False)

    class Meta():
        db_table = 'profiles'
        verbose_name = 'Профіль'
        verbose_name_plural = '🟥 Профілі'
        ordering = ['user__date_joined']

    def __str__(self):
        return f'Профіль ({self.user.username})'

    def get_absolute_url(self):
        return reverse('user:detail', args=[self.user.username])


class Subscribe(Model):
    user_from = ForeignKey(Profile, CASCADE, related_name='rel_from_set')
    user_to = ForeignKey(Profile, CASCADE, related_name='rel_to_set')
    created_date = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Підписка'
        verbose_name_plural = 'Підписки'
        unique_together = ('user_from', 'user_to')
        indexes = [Index(fields=['-created_date'])]
        ordering = ['-created_date']

    def __str__(self):
        return f'({self.user_from.user}) підписаний на ({self.user_to.user})'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
