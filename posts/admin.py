from django.utils.html import format_html
from django.contrib import admin
from django.forms import Textarea

from main.services import get_admin_html_image
from posts.models import PostType, PostTag, PostTopic, Post, PostComment


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['id', 'name', 'color', 'name_plural', 'slug']
    list_display_links = ['name']
    list_editable = ['slug', 'color']


@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'description']


@admin.register(PostTopic)
class PostTopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'is_general', 'slug', 'description']
    list_display_links = ['name']
    list_editable = ['is_general']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['user', 'total_likes', 'total_dislikes', 'total_saves']
    list_display = ['id', 'title', 'display_image', 'type', 'created_date']
    list_display_links = ['title']
    list_editable = ['type']
    list_filter = ['created_date', 'type', 'is_publicated']
    list_per_page = 20
    search_fields = ['title', 'content', 'meta_description']
    filter_horizontal = ('topics', 'tags')
    ordering = ['-created_date']
    date_hierarchy = 'created_date'
    
    fields = [
        ('user', 'type'),
        ('title', 'slug'),
        ('total_likes', 'total_dislikes', 'total_saves'),
        'content',
        'meta_description',
        ('image', 'detail_image'),
        'topics',
        'tags',
        ('is_publicated', 'review_rating'),
        ('review_pluses', 'review_minuses'),
    ]

    def save_model(self, request, obj, form, change):
        if not change or not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def display_image(self, obj: Post):
        if obj.image and obj.image.url:
            return format_html(
                get_admin_html_image(obj.image.url, obj, 'Дивитися на сайті'))

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(PostAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name in ['review_pluses', 'review_minuses']:
            field.widget = Textarea(attrs=field.widget.attrs)
        return field


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'user', 'is_edited', 'created_date']
    list_display_links = ['text']
    list_filter = ['created_date', 'is_active']
    list_per_page = 20
    readonly_fields = ['created_date', 'edit_date']
    search_fields = ['text']
    date_hierarchy = 'created_date'
    raw_id_fields = ['user', 'post', 'parent']

    fields = [
        ('user', 'post', 'parent'),
        'text',
        ('created_date', 'edit_date'),
        ('is_edited', 'is_active'),
    ]
