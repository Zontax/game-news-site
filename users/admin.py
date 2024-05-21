from django.utils.html import format_html
from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'is_active', 'first_name', 'last_name',
                    'email', 'is_superuser', 'display_avatar', 'date_joined']
    list_display_links = ['username']
    search_fields = ['username', 'first_name',
                     'last_name', 'email', 'phone_number']
    list_filter = ['date_joined', 'last_login']
    readonly_fields = ['username', 'email', 'phone_number',
                       'password', 'date_joined', 'last_login', 'is_superuser']

    fields = [
        ('username','last_login'),
        ('first_name', 'last_name'),
        ('avatar', 'profile_bg'),
        'description',
        ('email', 'phone_number'),
        'date_joined',
    ]
    
    def display_avatar(self, obj: User):
        if obj.avatar and obj.avatar.url:
            return format_html(
                f'''
                <a href="{obj.get_absolute_url()}" 
                    title="Переглянути профіль">
                    <img src="{obj.avatar.url}" width="50" height="50" />
                </a>''')
        return None
