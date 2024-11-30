from django.contrib import admin

from main.models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'description', 'disable_date']
    list_editable = ['description', 'is_active']

    fields = [
        'name',
        'description',
        'css_style',
        'image',
        'is_active',
    ]
