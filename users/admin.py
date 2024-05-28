from django.utils.html import format_html
from django.contrib import admin

from users.models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профілі'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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
                f'''
                <a href="{obj.get_absolute_url()}" 
                    title="Переглянути профіль">
                    <img src="{obj.profile.avatar.url}" width="40" height="40" />
                </a>''')
        return None


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
            return format_html(
                f'''
                <a href="{obj.get_absolute_url()}" 
                    title="Переглянути профіль">
                    <img src="{obj.avatar.url}" width="40" height="40" />
                </a>''')
        return None
