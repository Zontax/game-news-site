import logging
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.html import format_html
from django.db.models import ImageField
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action
from image_uploader_widget.widgets import ImageUploaderWidget
from main.admin import CustomAdmin
from main.services import get_admin_html_image
from users.models import Subscribe, User, Profile
from users.tasks import send_to_email


logger = logging.getLogger(__name__)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    formfield_overrides = {
        ImageField: {'widget': ImageUploaderWidget},
    }


@admin.register(User)
class UserAdmin(ExtraButtonsMixin, CustomAdmin):
    inlines = [ProfileInline]
    list_display = ['id', 'username', 'display_avatar', 'is_active', 'first_name', 'last_name',
                    'email', 'is_superuser', 'date_joined']
    list_display_links = ['username']
    filter_horizontal = ['groups', 'user_permissions']
    search_fields = ['username', 'first_name',
                     'last_name', 'email']
    list_filter = ['date_joined', 'last_login']
    readonly_fields = ['username', 'email', 'password',
                       'date_joined', 'last_login', 'is_superuser']
    list_per_page = 20

    fields = [
        ('username', 'last_login'),
        ('first_name', 'last_name'),
        'email',
        'date_joined',
        ('is_active', 'is_staff', 'is_superuser'),
        'groups',
        'user_permissions',
    ]

    def display_avatar(self, obj: User):
        if obj.profile.avatar and obj.profile.avatar.url:
            return format_html(
                get_admin_html_image(obj.profile.avatar.url, obj, 'Переглянути профіль'))

    @button(
        visible=lambda self: self.context['request'].user.is_superuser,
        html_attrs={'style': 'background-color:#DC6C6C;color:black'})
    def send_email(self, request):
        def _action(request):
            email = self.get_object(request)
            logger.info(email)
            subject = f'{settings.APP_NAME} - Повідомлення'
            message = 'Це тестове повідомлення з адміністративної панелі'
            html_message = f'<h1>{message}</h1>'
            send_to_email.delay(subject, message, html_message, email, False)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

        return confirm_action(
            modeladmin=self,
            request=request,
            action=_action,
            title='Надіслати email',
            message='Ви впевнені, що хочете надіслати електронний лист користувачеві?',
            success_message='Лист було успішно надіслано',
            error_message='Сталася помилка при надсиланні листа',
            description='Ця дія відправить лист власнику цього запису'
        )


@admin.register(Subscribe)
class SubscribeAdmin(CustomAdmin):
    list_display = ['created_date', 'user_from', 'user_to']
    readonly_fields = ['created_date']
    list_per_page = 20

    fields = [
        ('user_from', 'user_to'),
        'created_date'
    ]
