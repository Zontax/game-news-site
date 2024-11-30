from django.contrib import admin
from main.models import Announcement


class CustomAdmin(admin.ModelAdmin):
    """
    Custom ModelAdmin where disabled model logging
    """

    def log_addition(self, *args):
        return

    def log_change(self, *args):
        return

    def log_deletion(self, *args):
        return


@admin.register(Announcement)
class AnnouncementAdmin(CustomAdmin):
    list_display = ['name', 'is_active', 'description', 'disable_date']
    list_editable = ['description', 'is_active']

    fields = [
        'name',
        'description',
        'css_style',
        'image',
        'is_active',
    ]
