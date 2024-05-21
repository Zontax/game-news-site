from django.utils.html import format_html
from django.contrib import admin

from posts.models import PostType, PostTag, PostTopic, Post, PostComment


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'color', 'name_plural', 'slug']
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
    list_display = ['id', 'title', 'display_image', 'type', 'created_date']
    list_display_links = ['title']
    list_editable = ['type']
    list_filter = ['created_date', 'type']
    list_per_page = 20
    search_fields = ['title', 'content', 'meta_description']
    filter_horizontal = ('topics', 'tags')
    ordering = ['-created_date']
    date_hierarchy = 'created_date'
    raw_id_fields = ['user']
    
    fields = [
        ('user', 'type'),
        ('title', 'slug'),
        'content',
        'meta_description',
        ('image', 'detail_image'),
        'topics',
        'tags',
        'is_publicated',
    ]

    def display_image(self, obj: Post):
        if obj.image and obj.image.url:
            return format_html(
                f'''
                <a href="{obj.get_absolute_url()}" 
                    title="Дивитися на сайті">
                    <img src="{obj.image.url}" width="50" height="50" />
                </a>''')
        return None

    display_image.short_description = 'Icon'


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'user', 'is_edited', 'created_date']
    list_display_links = ['text']
    list_filter = ['created_date']
    list_per_page = 20
    search_fields = ['text']
    date_hierarchy = 'created_date'
    raw_id_fields = ['user', 'post', 'parent']
