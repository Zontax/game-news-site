from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_active', 'first_name', 'last_name',
                    'email', 'phone_number', 'is_superuser', 'date_joined']

    search_fields = ['username', 'first_name',
                     'last_name', 'email', 'phone_number']
    list_filter = ['date_joined', 'last_login']
    readonly_fields = ['username', 'email', 'phone_number',
                       'password', 'date_joined', 'last_login', 'is_superuser']

    fields = [
        'username',
        ('first_name', 'last_name'),
        ('avatar', 'profile_bg'),
        'email',
        'phone_number',
        'password',
        'date_joined',
        'last_login',
    ]
