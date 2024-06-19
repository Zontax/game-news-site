from django.utils.html import format_html
from django.contrib import admin

from main.services import get_admin_html_image
from users.models import Subscribe, User, Profile
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action, link, view
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профілі'


@admin.register(User)
class UserAdmin(ExtraButtonsMixin, admin.ModelAdmin):
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

    @button(visible=lambda self: self.context['request'].user.is_superuser,
            change_form=True,
            html_attrs={'style': 'background:#16941a;'})
    def refresh(self, request):
        self.message_user(request, 'refresh called')
        return HttpResponseRedirectToReferrer(request)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_avatar', 'phone_number']
    list_display_links = ['user']
    search_fields = ['user', 'phone_number']
    list_filter = ['user']
    readonly_fields = ['user']
    raw_id_fields = ['user']
    list_per_page = 20

    fields = [
        'user',
        'bio',
        ('phone_number', 'date_of_birth'),
        ('avatar', 'profile_bg')
    ]

    def display_avatar(self, obj: Profile):
        if obj.avatar and obj.avatar.url:
            return format_html(get_admin_html_image(obj.avatar.url, obj, 'Переглянути профіль'))


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['created_date', 'user_from', 'user_to']
    readonly_fields = ['created_date']
    list_per_page = 20

    fields = [
        ('user_from', 'user_to'),
        'created_date'
    ]
